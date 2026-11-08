import redis 

try: # Conexión a Redis Stack 
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True) 
    # 1. Comprobar PING 
    if r.ping(): 
        print("✅ Conexión con Redis establecida con éxito.") 
    # 2. Verificar módulo RedisJSON 
    r.json().set("test_clave", "$", {"estado": "ok", "mensaje": "Módulo JSON listo"}) 
    val = r.json().get("test_clave") 
    print(f"✅ Prueba de módulo JSON: {val}") 
    
    # Limpieza de la clave de prueba 
    r.delete("test_clave") 
    print("La infraestructura está lista para comenzar los ejercicios.") 

except Exception as e: 
    print(f"❌ Error al conectar con Redis: {e}")