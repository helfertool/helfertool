from django.conf import settings
from django.template.defaultfilters import date as date_f

from tempfile import mkdtemp, mkstemp
import os
import subprocess
import shutil

import badges.models


class BadgeCreatorError(Exception):
    def __init__(self, value, latex_output=None):
        self.value = value
        self.latex_output = latex_output

        Exception.__init__(self, value, latex_output)

    def __str__(self):
        return repr(self.value)


class BadgeCreator:
    def __init__(self, badgesettings):
        self.settings = badgesettings

        self.columns = self.settings.columns
        self.rows = self.settings.rows

        # list of helpers (dict with attributes)
        self.helpers = []

        # create temporary files
        self.dir = mkdtemp(dir=settings.TMP_ROOT, prefix="badges_")
        self.latex_file, self.latex_file_path = mkstemp(suffix='.tex',
                                                        dir=self.dir)

        # we copy the photos and background images to the temporary directory
        # pdflatex is only allowed to include files from there
        self.dir_photos = os.path.join(self.dir, 'photos')
        os.mkdir(self.dir_photos, mode=0o700)

        self.dir_backgrounds = os.path.join(self.dir, 'backgrounds')
        os.mkdir(self.dir_backgrounds, mode=0o700)

        # prevent that the same file is copied multiple times
        self._copied_files = []

    def add_helper(self, helper):
        tmp = {
            'firstname': self._latex_escape(helper.badge.firstname or helper.firstname),
            'surname': self._latex_escape(helper.badge.surname or helper.surname),
        }

        job = helper.badge.get_job()

        # job
        if helper.badge.job:
            tmp['job'] = self._latex_escape(helper.badge.job)
        elif job:
            tmp['job'] = self._latex_escape(job.name)
        else:
            tmp['job'] = ''

        # shift
        if helper.badge.shift:
            tmp['shift'] = self._latex_escape(helper.badge.shift)
        else:
            tmp['shift'] = self._latex_escape(self._get_shift_text(helper, job))

        # role
        if helper.badge.role:
            tmp['role'] = self._latex_escape(helper.badge.role)
        elif not helper.badge.no_default_role():
            if helper.is_coordinator:
                tmp['role'] = self._latex_escape(self.settings.coordinator_title)
            else:
                tmp['role'] = self._latex_escape(self.settings.helper_title)
        else:
            tmp['role'] = ""

        # photo
        if helper.badge.photo:
            tmp['photo'] = self._copy_photo(helper.badge.photo.path)
        else:
            tmp['photo'] = ''

        # design
        design = helper.badge.get_design()
        tmp['fontcolor'] = self._latex_color(design.font_color)
        tmp['bgcolor'] = self._latex_color(design.bg_color)

        if design.bg_front:
            tmp['bgfront'] = self._copy_background(design.bg_front.path)
        else:
            tmp['bgfront'] = ""

        if design.bg_back:
            tmp['bgback'] = self._copy_background(design.bg_back.path)
        else:
            tmp['bgback'] = ""

        # role
        role = helper.badge.get_role()
        tmp['roleid'] = role.latex_name

        # badge id
        if self.settings.barcodes:
            tmp['id'] = "%010d" % helper.badge.barcode
        else:
            tmp['id'] = ""

        # permissions
        all_permissions = badges.models.BadgePermission.objects.filter(badge_settings=self.settings.pk).all()
        selected_permissions = role.permissions
        for perm in all_permissions:
            if selected_permissions.filter(pk=perm.pk).exists():
                tmp['perm-%s' % perm.latex_name] = 'true'
            else:
                tmp['perm-%s' % perm.latex_name] = 'false'

        self.helpers.append(tmp)

    def generate(self):
        latex_code = self._get_latex()

        # read template
        try:
            f = self.settings.latex_template
            f.open('r')
            template = f.read()
            f.close()
        except IOError as e:
            raise BadgeCreatorError("Cannot open file \"%s\": %s" %
                                    (self.settings.latex_template.path,
                                     str(e)))

        # replace '%BADGEDATA%'
        latex = template.replace('%BADGEDATA%', latex_code)

        # write code
        try:
            f = os.fdopen(self.latex_file, 'w')
            f.write(latex)
            f.close()
        except IOError as e:
            raise BadgeCreatorError("Cannot write to file \"%s\": %s" %
                                    (self.latex_file_path, str(e)))

        # debug
        if settings.BADGE_TEMPLATE_DEBUG_FILE:
            shutil.copyfile(self.latex_file_path, settings.BADGE_TEMPLATE_DEBUG_FILE)

        # call pdflatex
        try:
            # only allow read in the directory of the tex file (and write, but this is default)
            env = os.environ
            env["openin_any"] = "p"
            env["openout_any"] = "p"
            env["TEXMFOUTPUT"] = self.dir

            subprocess.check_output([settings.BADGE_PDFLATEX,
                                     "-halt-on-error",
                                     "-no-shell-escape",
                                     "-output-directory", self.dir,
                                     os.path.basename(self.latex_file_path)],
                                    cwd=self.dir)
        except subprocess.CalledProcessError as e:
            raise BadgeCreatorError("PDF generation failed", e.output.decode('utf8'))

        # return path to pdf
        pdf_filename = "%s.pdf" % os.path.splitext(self.latex_file_path)[0]
        return self.dir, pdf_filename

    def finish(self):
        if os.path.isdir(self.dir):
            shutil.rmtree(self.dir)

    def _get_shift_text(self, helper, primary_job):
        """
        We create a string like: Shift 1, Shift 2 (Other job), Shift 3
        Depending on the settings, we use the shift name (if available) or the time in a certain format.
        The job is added if it is not the primary job.

        Returns the text (not LaTeX escaped!)
        """
        shift_texts = []
        for shift in helper.shifts.all().order_by('begin'):
            # get shift date / name
            cur_text = ""
            if not self.settings.shift_no_names and shift.name:
                # we want to use a name and have one
                cur_text = shift.name
            else:
                # use time. format depends on settings, but we always needs the time
                cur_text = shift.time_hours()

                # the date format depends on the settings
                date_format_string = None
                if self.settings.shift_format == badges.models.BadgeSettings.SHIFT_FORMAT_DATE:
                    date_format_string = "d.m"
                elif self.settings.shift_format == badges.models.BadgeSettings.SHIFT_FORMAT_WEEKDAY:
                    date_format_string = "D"

                # add the date, if we want to
                if date_format_string:
                    cur_text = "{} {}".format(date_f(shift.date(), date_format_string), cur_text)

            # add job if it is not the primary job
            if shift.job != primary_job:
                cur_text = "{} ({})".format(cur_text, shift.job.name)

            shift_texts.append(cur_text)

        return ', '.join(shift_texts)

    def _get_latex(self):
        # whitespace, if code would be empty
        if len(self.helpers) == 0:
            return r'\ '

        r = ''

        # number of badges on one page
        num_page = self.columns*self.rows

        page = 1
        while (page-1)*num_page < len(self.helpers):
            # helper for this page
            data_for_page = self.helpers[(page-1)*num_page:page*num_page]

            # front side
            r = r + self._create_table('badgefront', data_for_page)

            # back
            r = r + self._create_table('badgeback', data_for_page, True)

            # next page
            page = page + 1

        return r

    def _create_badge_side(self, latex_command, helper_data):
        data = ",".join(["%s=%s" % (key, helper_data[key]) for key in
                         helper_data])
        template = r'\%s[%s]' % (latex_command, data)

        return template

    def _create_table(self, latex_command, helpers_data, reverse_rows=False):
        r = ''

        # begin of table
        r = r + r'\begin{tabular}{|l|l|}' + "\n"
        r = r + r'\hline' + "\n"

        # add rows until all helpers were added
        row = 1
        while (row-1)*self.columns < len(helpers_data):
            # get helpers for this row
            data_for_row = helpers_data[(row-1)*self.columns:row*self.columns]

            latex_for_row = [self._create_badge_side(latex_command, h) for h in
                             data_for_row]

            # fill row if necessary
            while len(latex_for_row) < self.columns:
                latex_for_row.append("")

            # reverse?
            if reverse_rows:
                latex_for_row.reverse()

            # insert ' & ' between items, add '\\' and linebreak
            latex_row = ' & '.join(latex_for_row) + r' \\' + "\n"

            # add to result
            r = r + latex_row

            # add hline
            r = r + r'\hline' + "\n"

            # next row
            row = row + 1

        # end of table
        r = r + r'\end{tabular}' + "\n"

        # page break
        r = r + "\n" + r'\pagebreak' + "\n\n"

        return r

    def _latex_color(self, string):
        # latex expects HTML colors without '#' and uppercase

        if string.startswith('#'):
            string = string[1:]
        return string.upper()

    def _latex_escape(self, string):
        string = string.replace('\\', r'\textbackslash ')
        string = string.replace(r' ', r'\ ')
        string = string.replace(r'&', r'\&')
        string = string.replace(r'%', r'\%')
        string = string.replace(r'$', r'\$')
        string = string.replace(r'#', r'\#')
        string = string.replace(r'_', r'\_')
        string = string.replace(r'{', r'\{')
        string = string.replace(r'}', r'\}')
        string = string.replace(r'~', r'\textasciitilde ')
        string = string.replace(r'^', r'\textasciicircum ')

        return '{' + string + '}'

    def _copy_photo(self, src_path):
        return self._copy_file(src_path, self.dir_photos)

    def _copy_background(self, src_path):
        return self._copy_file(src_path, self.dir_backgrounds)

    def _copy_file(self, src_path, dest_folder):
        filename = os.path.basename(src_path)
        dest_path = os.path.join(dest_folder, filename)

        if src_path not in self._copied_files:
            shutil.copyfile(src_path, dest_path)
            self._copied_files.append(src_path)

        return os.path.relpath(dest_path, self.dir)
