from app import models
models.User.query.delete()
models.Products.query.delete()