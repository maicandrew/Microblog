from app import create_app, db, cli
'''Import the Application Factory function, database handling object
    and commands for translate'''
from app.models import User, Post

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_coontext():
    return {'db': db, 'User': User, 'Post': Post}