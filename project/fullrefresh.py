# project/fullrefresh.py

from api.request import token_refresh
from entity.product import product

# get new token here
token = token_refresh()
# tutaj get token i puscic wszystkie
# product(token = token, action = 'POST')

product(token=token, action='post')
product(token=token, action='put')
product(token=token, action='delete')



