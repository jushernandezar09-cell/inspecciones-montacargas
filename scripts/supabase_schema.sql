-- Ejecuta este script UNA VEZ en tu proyecto de Supabase:
-- Panel de Supabase -> SQL Editor -> New query -> pega esto -> Run.
--
-- Crea la tabla que guarda cada fila (día + turno) de la hoja de
-- inspección de montacargas. La app (backend en Python) se conecta
-- directo a esta base con SQLAlchemy usando la cadena de conexión de
-- Supabase (Connection string -> URI), no usa las llaves anon/service ni
-- el cliente supabase-js — por eso NO hace falta configurar Row Level
-- Security aquí: solo el backend tiene la contraseña de conexión.

create table if not exists public.inspecciones_montacargas (
    id                       bigint generated always as identity primary key,

    codigo_equipo            varchar(80)  not null,
    anio                     integer      not null,
    mes                      integer      not null,
    dia                      integer      not null,
    turno                    varchar(1)   not null,

    responsable_revision     varchar(150) not null default '',

    -- Mecanica
    cadenas_rodillos         varchar(5)   not null default '',
    nivel_aceite_frenos      varchar(5)   not null default '',
    fugas_aceite             varchar(5)   not null default '',
    freno_mano               varchar(5)   not null default '',
    horas_registradas        varchar(20)  not null default '',
    juego_pedales            varchar(5)   not null default '',

    -- Cabina Montacargas
    mandos_hidraulicos       varchar(5)   not null default '',
    temperatura_rango        varchar(5)   not null default '',
    instrumentos_panel       varchar(5)   not null default '',
    direccionales            varchar(5)   not null default '',

    -- Seguridad
    mecanismos_seguridad     varchar(5)   not null default '',
    luces_freno_marcha       varchar(5)   not null default '',
    extintor                 varchar(5)   not null default '',

    -- Estado de correccion
    se_corrige               varchar(5)   not null default '',
    responsable_correccion   varchar(150) not null default '',
    fecha_correccion         varchar(20)  not null default '',

    actualizado_en           timestamp    not null default now(),

    constraint uq_hoja_dia_turno unique (codigo_equipo, anio, mes, dia, turno)
);

create index if not exists ix_inspecciones_montacargas_codigo_equipo
    on public.inspecciones_montacargas (codigo_equipo);
create index if not exists ix_inspecciones_montacargas_anio
    on public.inspecciones_montacargas (anio);
create index if not exists ix_inspecciones_montacargas_mes
    on public.inspecciones_montacargas (mes);

-- Nota para cuando el documento F01-I28-P-IF-02 se revise formalmente y
-- cambie/agregue una columna del checklist: agrega la columna nueva aquí
-- con un ALTER TABLE, por ejemplo:
--   alter table public.inspecciones_montacargas
--     add column nueva_columna varchar(5) not null default '';
-- y agrégala también en app/modules/inspecciones_montacargas/formulario.py
-- y app/modules/inspecciones_montacargas/models.py (mismo nombre de clave).
