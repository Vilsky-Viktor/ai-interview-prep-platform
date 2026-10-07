class KeyRejected(Exception):
    """The ATS refused the company's key (wrong, revoked, expired or missing a permission): the
    connection needs a new one."""
