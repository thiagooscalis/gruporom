from fabric import Connection
from invoke import task


BASE_DIR = "/home/thiago/gruporom"


@task
def deploy(context, msg):
    conn = Connection("gruporom.lupa.dev.br")
    generate_requirements(conn)
    local_git(conn, msg)
    git_pull(conn)
    venv_tasks(conn)
    restart_services(conn)


def generate_requirements(conn):
    conn.local("uv export --no-dev > requirements.txt")


def git_pull(conn):
    with conn.cd(BASE_DIR):
        conn.run("git pull origin master", warn=True)


def venv_tasks(conn):
    pipinstall = "./.venv/bin/pip install --extra-index-url https://pypi."
    pipinstall += "python.org/simple -r requirements.txt"
    with conn.cd(BASE_DIR):
        conn.run("python3 -m venv .venv")
        conn.run(pipinstall)
        conn.run("./.venv/bin/python ./manage.py migrate")
        conn.run("./.venv/bin/python ./manage.py collectstatic --no-input")


def restart_services(conn):
    with conn.cd(BASE_DIR):
        conn.run("sudo supervisorctl restart gruporom:gruporom-daphne")
        conn.run("sudo supervisorctl restart gruporom:gruporom-workers")
        conn.run("sudo service nginx reload")


def local_git(conn, msg):
    conn.local("git add -A")
    conn.local(f'git commit -m "{msg}"')
    conn.local("git push origin master")
