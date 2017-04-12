import os
import subprocess
from latex.build import PdfLatexBuilder
from django.template.loader import get_template

def pdflatex(texfile, context, pdfout):
    template = get_template(texfile)
    rendered = template.render(context).encode('utf8')
    tex_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'templates', 'tex')
    pdf = PdfLatexBuilder(pdflatex='pdflatex').build_pdf(rendered,
                                                         texinputs=[tex_path, ''])
    pdf.save_to(pdfout)

