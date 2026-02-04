import oracledb, os, dotenv

dotenv.load_dotenv()

def get_pool():
    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")
    mode = os.getenv("ORACLE_MODE")

    auth_mode = oracledb.AUTH_MODE_SYSDBA if mode == "sysdba" else None

    return oracledb.create_pool(
        user=user,
        password=password,
        dsn=dsn,
        min=1,
        max=5,
        increment=1,
        privileged_name=auth_mode
    )

pool = get_pool()