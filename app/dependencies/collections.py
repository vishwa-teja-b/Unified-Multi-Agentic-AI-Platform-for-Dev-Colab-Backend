from fastapi import Request

# EXAMPLES : 
# def get_items_collection(request: Request):
#     return request.app.state.db["items"]

# def get_users_collection(request: Request):
#     return request.app.state.db["users"]

# def get_orders_collection(request: Request):
#     return request.app.state.db["orders"]

def get_profiles_collection(request: Request):
    return request.app.state.db["profiles"]

def get_projects_collection(request: Request):
    return request.app.state.db["projects"]

def get_invitations_collection(request: Request):
    return request.app.state.db["invitations"]

def get_teams_collection(request: Request):
    return request.app.state.db["teams"]

def get_project_plans_collection(request: Request):
    return request.app.state.db["project_plans"]

def get_rooms_collection(request: Request):
    return request.app.state.db["rooms"]
