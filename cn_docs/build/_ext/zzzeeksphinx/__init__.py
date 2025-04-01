__version__ = "1.5.2"


def setup(app):
    from . import (
        autodoc_mods,
        dialect_info,
        mako,
        sqlformatter,
        viewsource,
        scss,
        render_pydomains,
        extras,
    )

    # we use jquery.  See
    # https://www.sphinx-doc.org/en/master/changes.html#id65
    app.setup_extension("sphinxcontrib.jquery")

    # autodoc_mods.setup(app)
    # dialect_info.setup(app)
    # mako.setup(app)
    # sqlformatter.setup(app)
    viewsource.setup(app)  # 源文件读取
    # scss.setup(app)
    render_pydomains.setup(app) # 引用缩写
    extras.setup(app) # 额外指令

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
