-- Creación de la base de datos 
CREATE DATABASE IF NOT EXISTS datagob; 
USE datagob;

-- 1. Tabla: Partido politico 
CREATE TABLE partido_politico (
    id INT PRIMARY KEY, 
    nombre VARCHAR(255) NOT NULL, 
    cif VARCHAR(50) NOT NULL UNIQUE, 
    tipo_entidad VARCHAR(100) 
);

-- 2. Tabla: Entidad privada 
CREATE TABLE entidad_privada ( 
    id INT PRIMARY KEY, 
    cif VARCHAR(50) NOT NULL UNIQUE, 
    razon_social VARCHAR(255) NOT NULL, 
    cod_nace VARCHAR(150) NOT NULL -- Que representa el sector de actividad
);

-- 3. Tabla: Cargo politico 
CREATE TABLE cargo_politico ( 
    id INT PRIMARY KEY, 
    id_partido INT NOT NULL, 
    nombre_completo VARCHAR(255) NOT NULL, 
    dni_hash VARCHAR(255) NOT NULL, 
    puesto VARCHAR(150), 
    fecha_toma DATE, 
    fecha_cese DATE, 
    nivel_gobierno VARCHAR(100), 
    CONSTRAINT fk_cargo_partido FOREIGN KEY (id_partido) REFERENCES partido_politico(id) 
);

-- 4. Tabla: Declaración bienes 
CREATE TABLE declaracion_bienes ( 
    id INT PRIMARY KEY, 
    id_cargo INT NOT NULL, 
    fecha DATE NOT NULL, 
    ejercicio_fiscal INT NOT NULL, -- Expresado en AÑOS (ver si existe un tipo mejor)
    patrimonio_bruto DECIMAL(15, 2), 
    deudas_totales DECIMAL(15, 2), 
    participaciones_emp_valor DECIMAL(15, 2), -- Valor económico de acciones, participaciones o propiedades 
    CONSTRAINT fk_declaracion_cargo FOREIGN KEY (id_cargo) REFERENCES cargo_politico(id) 
);

-- 5. Tabla: Historial empleo privado 
CREATE TABLE historial_empleo_privado ( 
    id INT PRIMARY KEY, 
    id_cargo INT NOT NULL, 
    id_entidad INT NOT NULL, 
    puesto VARCHAR(150), 
    fecha_inicio DATE, 
    fecha_fin DATE, 
    CONSTRAINT fk_historial_cargo FOREIGN KEY (id_cargo) REFERENCES cargo_politico(id), 
    CONSTRAINT fk_historial_entidad FOREIGN KEY (id_entidad) REFERENCES entidad_privada(id) 
); 

-- 6. Tabla: Sanción Inhabilitante 
CREATE TABLE sancion_inhabilitante ( 
    id INT PRIMARY KEY, 
    id_entidad INT, -- NULLEABLE, ya que existen otras sanciones 
    tipo_infraccion VARCHAR(255), 
    fecha_inicio_sancion DATE, 
    duracion_veto INT, -- Expresada en meses
    CONSTRAINT fk_sancion_entidad FOREIGN KEY (id_entidad) REFERENCES entidad_privada(id) 
); 

-- 7. Tabla: Subvención pública 
CREATE TABLE subvencion_publica ( 
    id INT PRIMARY KEY, 
    id_entidad INT NOT NULL, 
    monto_concedido DECIMAL(15, 2), 
    programa_presupuestario VARCHAR(255), 
    fecha_concesion DATE, 
    concesion_directa BOOLEAN, 
    CONSTRAINT fk_subvencion_entidad FOREIGN KEY (id_entidad) REFERENCES entidad_privada(id) 
); 

-- 8. Tabla: Donaciones 
CREATE TABLE donaciones ( 
    id INT PRIMARY KEY, 
    id_partido INT NOT NULL, 
    id_entidad INT NOT NULL, 
    fecha DATE NOT NULL, 
    tipo_donacion VARCHAR(100), 
    monto DECIMAL(15, 2), 
    CONSTRAINT fk_donaciones_partido FOREIGN KEY (id_partido) REFERENCES partido_politico(id), 
    CONSTRAINT fk_donaciones_entidad FOREIGN KEY (id_entidad) REFERENCES entidad_privada(id) 
); 

-- 9. Tabla: Agente Lobby 
CREATE TABLE agente_lobby ( 
    id INT PRIMARY KEY, 
    id_entidad INT NOT NULL, 
    nombre_representante VARCHAR(255), 
    num_reg_lobby VARCHAR(100), -- Número de registro del lobby
    CONSTRAINT fk_agente_entidad FOREIGN KEY (id_entidad) REFERENCES entidad_privada(id) 
); 

-- 10. Tabla: Reuniones Lobby 
CREATE TABLE reuniones_lobby ( 
    id INT PRIMARY KEY, 
    id_cargo INT NOT NULL, 
    id_lobbyista INT NOT NULL, 
    fecha DATE NOT NULL, 
    materia_tratada TEXT, 
    exp_normativo_rel VARCHAR(255), -- Expediente normativo relacionado
    CONSTRAINT fk_reuniones_cargo FOREIGN KEY (id_cargo) REFERENCES cargo_politico(id), 
    CONSTRAINT fk_reuniones_lobbyista FOREIGN KEY (id_lobbyista) REFERENCES agente_lobby(id) 
);