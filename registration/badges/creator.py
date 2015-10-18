from django.conf import settings
from ..models import BadgePermission

from tempfile import mkdtemp, mkstemp
import os
import subprocess
import shutil


class BadgeCreatorError(Exception):
    def __init__(self, value, latex_output=None):
        self.value = value
        self.latex_output = latex_output

    def is_latex_output(self):
        return self.latex_output is not None

    def get_latex_output(self):
        return self.latex_output

    def __str__(self):
        return repr(self.value)


class BadgeCreator:
    def __init__(self, settings):
        self.settings = settings

        self.columns = self.settings.columns
        self.rows = self.settings.rows

        # list of helpers (dict with attributes)
        self.helpers = []

        # create temporary files
        self.dir = mkdtemp()
        self.latex_file, self.latex_filename = mkstemp(suffix='.tex',
                                                       dir=self.dir)

    def add_helper(self, helper):
        tmp = {'prename': helper.badge.prename or helper.prename,
               'surname': helper.badge.surname or helper.surname,
               'shift': helper.badge.shift}

        job = helper.badge.get_job()

        # job
        if helper.badge.job:
            tmp['job'] = helper.badge.job
        elif job:
            tmp['job'] = job.name
        else:
            tmp['job'] = ''

        # role
        if helper.badge.role:
            tmp['role'] = helper.badge.role
        elif helper.is_coordinator:
            tmp['role'] = self.settings.coordinator_title
        else:
            tmp['role'] = self.settings.helper_title

        # photo
        if helper.badge.photo:
            tmp['photo'] = helper.badge.photo.path
        else:
            tmp['photo'] = ''

        # design
        design = helper.badge.get_design()
        tmp['bgfront'] = design.bg_front.path
        tmp['bgback'] = design.bg_back.path
        tmp['fontcolor'] = self._latex_color(design.font_color)

        # role
        role = helper.badge.get_role()
        tmp['roleid'] = role.latex_name

        # permissions
        all_permissions = BadgePermission.objects.filter(
            badge_settings=self.settings).all()
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
            template = f.read().decode('utf-8')
            f.close()
        except IOError as e:
            raise BadgeCreatorError("Cannot open file \"%s\": %s" %
                                    (self.settings.latex_template.path,
                                     str(e)))

        # replace '%BADGEDATA%'
        latex = template.replace('%BADGEDATA%', latex_code)

        # write code
        try:
            f = open(self.latex_file, 'w')
            f.write(latex)
            f.close()
        except IOError as e:
            raise BadgeCreatorError("Cannot write to file \"%s\": %s" %
                                    (self.latex_filename, str(e)))

        # debug
        if settings.BADGE_TEMPLATE_DEBUG_FILE:
            shutil.copyfile(self.latex_filename,
                            settings.BADGE_TEMPLATE_DEBUG_FILE)

        # call pdflatex
        try:
            subprocess.check_output(["pdflatex", "-halt-on-error",
                                     "-output-directory", self.dir,
                                     self.latex_filename])
        except subprocess.CalledProcessError as e:
            raise BadgeCreatorError("PDF generation failed", e.output)

        # return path to pdf
        return "%s.pdf" % os.path.splitext(self.latex_filename)[0]

    def finish(self):
        shutil.rmtree(self.dir)

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
            r = r + '\hline' + "\n"

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
