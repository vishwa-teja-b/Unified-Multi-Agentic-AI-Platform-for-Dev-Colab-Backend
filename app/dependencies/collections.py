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
