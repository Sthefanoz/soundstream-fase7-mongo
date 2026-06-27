"""
Generacion de ids enteros secuenciales para las colecciones de MongoDB.

Los documentos existentes usan '_id' entero (no ObjectId), asi que al insertar
nuevos documentos calculamos el siguiente id como max(_id) + 1. Es el
equivalente NoSQL al IDENTITY/autoincrement de SQL.
"""


def siguiente_id(modelo):
    ultimo = (modelo.objects.order_by('-pk')
              .values_list('pk', flat=True).first())
    return (ultimo or 0) + 1
