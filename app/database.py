import oracledb, os, dotenv

dotenv.load_dotenv()

def get_pool():
    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")
    mode_str = os.getenv("ORACLE_MODE")

    # Map sysdba string to the correct driver constant
    auth_mode = oracledb.AUTH_MODE_DEFAULT
    if mode_str and mode_str.lower() == "sysdba":
        auth_mode = oracledb.AUTH_MODE_SYSDBA

    return oracledb.create_pool(
        user=user,
        password=password,
        dsn=dsn,
        min=1,
        max=5,
        increment=1,
        mode=auth_mode  # Use 'mode' instead of 'privileged_name'
    )

pool = get_pool()