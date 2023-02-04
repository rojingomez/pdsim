# -*- coding: utf-8 -*-
#
# PDModel documentation build configuration file, created by
# sphinx-quickstart on Wed May 02 18:01:14 2012.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys, os, subprocess

on_rtd = os.getenv('READTHEDOCS') == 'True'

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#sys.path.insert(0, os.path.abspath('sphinxext'))

# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

#sys.path.insert(0,os.path.abspath('..'))
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath(os.path.join('..','GUI')))

def run_prebuild(_):

    # Run sphinx.apidoc programmatically to autogenerate documentation for PDSim
    from sphinx.ext.apidoc import main
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    output_path = os.path.join(cur_dir, 'PDSim_apidoc')
    main(argv=['-e', '-o', output_path, os.path.dirname(PDSim.__file__), '--force'])

    # -- Execute all notebooks --------------------------------------------------
    if on_rtd:
        for path, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.ipynb') and '.ipynb_checkpoints' not in path:
                    subprocess.check_output(f'jupyter nbconvert  --to notebook --output {file} --execute {file}', shell=True, cwd=path)
                    # --ExecutePreprocessor.allow_errors=True      (this allows you to allow errors globally, but a raises-exception cell tag is better)

    # # Convert the notebooks to RST
    # nb_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'notebooks')
    # nb_index_fname = os.path.join(nb_dir, 'index.rst')
    # if not os.path.exists(nb_index_fname):
    #   print('converting jupyter notebooks to RST')
    #   sys.path.append(nb_dir)
    #   import compile_notebooks
    #   compile_notebooks.convert_notebooks()

def setup(app):
    app.connect('builder-inited', run_prebuild)
              
extensions = ['nbsphinx',
              'sphinx.ext.autodoc', 
              'sphinx.ext.napoleon',
              'sphinx.ext.intersphinx', 
              #~ 'sphinx.ext.coverage',
              'sphinx.ext.autosummary', 
              'sphinx.ext.viewcode',
              'sphinx.ext.mathjax',
              'matplotlib.sphinxext.plot_directive',
              'IPython.sphinxext.ipython_console_highlighting',
              'IPython.sphinxext.ipython_directive'
              ]              

#autodoc_default_flags = ['members','no-inherited-members','show-inheritance','private-members']

intersphinx_mapping = {'CoolProp': ('http://coolprop.sourceforge.net', None),
                       'matplotlib':('https://matplotlib.org', None),
                       'wx': ('http://wxpython.org/Phoenix/docs/html/', None),
                       'python': ('https://docs.python.org/3/',None),
                       'numpy':('https://docs.scipy.org/doc/numpy',None)
                       }

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'PDSim'
copyright = u'2012, Ian Bell'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
import PDSim
# The short X.Y version.
version = PDSim.__version__
# The full version, including alpha/beta/rc tags.
release = version

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    html_theme = 'default'
else:
    html_theme = 'nature'
    
    import sphinx_bootstrap_theme
    # Activate the theme.
    html_theme = 'bootstrap'
    html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
    # Theme options are theme-specific and customize the look and feel of a
    # theme further.
    html_theme_options = {
        # Navigation bar title. (Default: ``project`` value)
        'navbar_title': "PDSim",

        # Tab name for entire site. (Default: "Site")
        'navbar_site_name': "Site",

        # A list of tuples containing pages or urls to link to.
        # Valid tuples should be in the following forms:
        #    (name, page)                 # a link to a page
        #    (name, "/aa/bb", 1)          # a link to an arbitrary relative url
        #    (name, "http://example.com", True) # arbitrary absolute url
        # Note the "1" or "True" value above as the third argument to indicate
        # an arbitrary url.
        'navbar_links': [
            ("API", "PDSim_apidoc/PDSim"),
            #("Link", "http://example.com", True),
        ],

        # Render the next and previous page links in navbar. (Default: true)
        'navbar_sidebarrel': True,

        # Render the current pages TOC in the navbar. (Default: true)
        'navbar_pagenav': True,

        # Global TOC depth for "site" navbar tab. (Default: 1)
        # Switching to -1 shows all levels.
        'globaltoc_depth': 2,

        # Include hidden TOCs in Site navbar?
        #
        # Note: If this is "false", you cannot have mixed ``:hidden:`` and
        # non-hidden ``toctree`` directives in the same page, or else the build
        # will break.
        #
        # Values: "true" (default) or "false"
        'globaltoc_includehidden': "true",

        # HTML navbar class (Default: "navbar") to attach to <div> element.
        # For black navbar, do "navbar navbar-inverse"
        'navbar_class': "navbar navbar-inverse",

        # Fix navigation bar to top of page?
        # Values: "true" (default) or "false"
        'navbar_fixed_top': "true",

        # Location of link to source.
        # Options are "nav" (default), "footer" or anything else to exclude.
        'source_link_position': "nav",

        # Bootswatch (http://bootswatch.com/) theme.
        #
        # Options are nothing with "" (default) or the name of a valid theme
        # such as "amelia" or "cosmo".
        'bootswatch_theme': "yeti",

        # Choose Bootstrap version.
        # Values: "3" (default) or "2" (in quotes)
        'bootstrap_version': "3",
        
    }

#~ import sphinx_rtd_theme
#~ html_theme = "sphinx_rtd_theme"
#~ html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

#~ sys.path.append(os.path.abspath('_themes'))
#~ html_theme_path = ['_themes']
#~ html_theme = 'kr'

#~ import sphinx_readable_theme
#~ html_theme_path = [sphinx_readable_theme.get_html_theme_path()]
#~ html_theme = 'readable'

#~ # import Cloud
#~ import cloud_sptheme as csp
#~ # set the html theme
#~ html_theme = "cloud" # NOTE: there is also a red-colored version named "redcloud"
#~ # set the theme path to point to cloud's theme data
#~ html_theme_path = [csp.get_theme_dir()]
#~ # [optional] set some of the options listed above...
#~ html_theme_options = { "roottarget": "index" }


#html_theme = 'Cloud'
#html_theme_path = ['../externals/scipy-sphinx-theme/_theme']
# html_theme_options = {
#     "edit_link": "true",
#     "sidebar": "right",
#     "scipy_org_logo": "false",
#     "rootlinks": [("http://scipy.org/", "Scipy.org"),
#                   ("http://docs.scipy.org/", "Docs")]
# }

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'PDSimdoc'


# -- Options for LaTeX output --------------------------------------------------

# The paper size ('letter' or 'a4').
#latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'PDSim.tex', u'PDModel Documentation',
   u'Ian Bell', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'pdsim', u'PDSim Documentation',
     [u'Ian Bell'], 1)
]



