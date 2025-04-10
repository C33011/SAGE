"""
Basic tests to make sure the package can be imported and the version is set.
"""

def test_import():
    """Test that the package can be imported"""
    import sage
    assert sage is not None


def test_version():
    """Test that the version number is set"""
    from sage.version import __version__
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__.split('.')) >= 2
