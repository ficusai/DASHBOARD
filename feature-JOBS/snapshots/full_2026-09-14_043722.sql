--
-- PostgreSQL database dump
--

\restrict SUSDVa32bgc9LcUSs1Brtur92rhLM3iaj1sRmXSDJcQaRU7YUFGMia8IIprRdVX

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: event_kind; Type: TYPE; Schema: public; Owner: ficus
--

CREATE TYPE public.event_kind AS ENUM (
    'import',
    'claim',
    'complete',
    'fail',
    'retry',
    'reclaim',
    'human_edit',
    'cancel'
);


ALTER TYPE public.event_kind OWNER TO ficus;

--
-- Name: task_status; Type: TYPE; Schema: public; Owner: ficus
--

CREATE TYPE public.task_status AS ENUM (
    'pending',
    'running',
    'completed',
    'error',
    'failed',
    'skipped'
);


ALTER TYPE public.task_status OWNER TO ficus;

--
-- Name: task_type; Type: TYPE; Schema: public; Owner: ficus
--

CREATE TYPE public.task_type AS ENUM (
    'single_change',
    'single_create',
    'single_check',
    'single_verify'
);


ALTER TYPE public.task_type OWNER TO ficus;

--
-- Name: verification_method; Type: TYPE; Schema: public; Owner: ficus
--

CREATE TYPE public.verification_method AS ENUM (
    'file_exists',
    'regex_match',
    'shell_cmd',
    'json_schema',
    'diff_contains',
    'manual'
);


ALTER TYPE public.verification_method OWNER TO ficus;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: models_allowed; Type: TABLE; Schema: public; Owner: ficus
--

CREATE TABLE public.models_allowed (
    name text NOT NULL,
    size_mb integer,
    enabled boolean DEFAULT true NOT NULL,
    notes text
);


ALTER TABLE public.models_allowed OWNER TO ficus;

--
-- Name: system_state; Type: TABLE; Schema: public; Owner: ficus
--

CREATE TABLE public.system_state (
    key text NOT NULL,
    value jsonb NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.system_state OWNER TO ficus;

--
-- Name: tags_allowed; Type: TABLE; Schema: public; Owner: ficus
--

CREATE TABLE public.tags_allowed (
    name text NOT NULL,
    description text
);


ALTER TABLE public.tags_allowed OWNER TO ficus;

--
-- Name: task_events; Type: TABLE; Schema: public; Owner: ficus
--

CREATE TABLE public.task_events (
    id bigint NOT NULL,
    task_id uuid NOT NULL,
    kind public.event_kind NOT NULL,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.task_events OWNER TO ficus;

--
-- Name: task_events_id_seq; Type: SEQUENCE; Schema: public; Owner: ficus
--

ALTER TABLE public.task_events ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.task_events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: ficus
--

CREATE TABLE public.tasks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    priority integer DEFAULT 0 NOT NULL,
    type public.task_type NOT NULL,
    title text NOT NULL,
    instruction text NOT NULL,
    expected_output text NOT NULL,
    target_path text NOT NULL,
    context_files jsonb DEFAULT '[]'::jsonb NOT NULL,
    verification_method public.verification_method NOT NULL,
    verification_spec text NOT NULL,
    timeout_sec integer DEFAULT 30 NOT NULL,
    model_hint text,
    max_tokens integer DEFAULT 512 NOT NULL,
    retry_count integer DEFAULT 0 NOT NULL,
    max_retries integer DEFAULT 2 NOT NULL,
    tags jsonb DEFAULT '[]'::jsonb NOT NULL,
    depends_on jsonb DEFAULT '[]'::jsonb NOT NULL,
    status public.task_status DEFAULT 'pending'::public.task_status NOT NULL,
    started_at timestamp with time zone,
    finished_at timestamp with time zone,
    locked_by text,
    heartbeat_at timestamp with time zone,
    result jsonb,
    error_text text,
    embedding public.vector(768),
    CONSTRAINT tasks_expected_output_check CHECK ((length(expected_output) <= 500)),
    CONSTRAINT tasks_instruction_check CHECK ((length(instruction) <= 280)),
    CONSTRAINT tasks_max_retries_check CHECK (((max_retries >= 0) AND (max_retries <= 3))),
    CONSTRAINT tasks_max_tokens_check CHECK (((max_tokens >= 1) AND (max_tokens <= 1024))),
    CONSTRAINT tasks_timeout_sec_check CHECK (((timeout_sec >= 1) AND (timeout_sec <= 120))),
    CONSTRAINT tasks_title_check CHECK ((length(title) <= 200))
);


ALTER TABLE public.tasks OWNER TO ficus;

--
-- Data for Name: models_allowed; Type: TABLE DATA; Schema: public; Owner: ficus
--

COPY public.models_allowed (name, size_mb, enabled, notes) FROM stdin;
qwen2.5:0.5b	398	t	tiny default — first choice for atomic tasks
llama3.2:1b	1300	t	fallback for slightly larger reasoning
phi3-mini	2200	t	opt-in only, slower
\.


--
-- Data for Name: system_state; Type: TABLE DATA; Schema: public; Owner: ficus
--

COPY public.system_state (key, value, updated_at) FROM stdin;
worker_id	"fedora-worker-01"	2026-09-14 03:54:18.382781+03
current_model	"qwen2.5:0.5b"	2026-09-14 03:54:18.382781+03
last_poll_at	null	2026-09-14 03:54:18.382781+03
paused	false	2026-09-14 03:54:18.382781+03
schema_version	"1.0.0"	2026-09-14 03:54:18.382781+03
\.


--
-- Data for Name: tags_allowed; Type: TABLE DATA; Schema: public; Owner: ficus
--

COPY public.tags_allowed (name, description) FROM stdin;
docs	documentation edits
lint	style / formatting fixes
test	test file creation
refactor	small structural change
check	read-only verification task
\.


--
-- Data for Name: task_events; Type: TABLE DATA; Schema: public; Owner: ficus
--

COPY public.task_events (id, task_id, kind, payload, at) FROM stdin;
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: ficus
--

COPY public.tasks (id, created_at, priority, type, title, instruction, expected_output, target_path, context_files, verification_method, verification_spec, timeout_sec, model_hint, max_tokens, retry_count, max_retries, tags, depends_on, status, started_at, finished_at, locked_by, heartbeat_at, result, error_text, embedding) FROM stdin;
\.


--
-- Name: task_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ficus
--

SELECT pg_catalog.setval('public.task_events_id_seq', 1, false);


--
-- Name: models_allowed models_allowed_pkey; Type: CONSTRAINT; Schema: public; Owner: ficus
--

ALTER TABLE ONLY public.models_allowed
    ADD CONSTRAINT models_allowed_pkey PRIMARY KEY (name);


--
-- Name: system_state system_state_pkey; Type: CONSTRAINT; Schema: public; Owner: ficus
--

ALTER TABLE ONLY public.system_state
    ADD CONSTRAINT system_state_pkey PRIMARY KEY (key);


--
-- Name: tags_allowed tags_allowed_pkey; Type: CONSTRAINT; Schema: public; Owner: ficus
--

ALTER TABLE ONLY public.tags_allowed
    ADD CONSTRAINT tags_allowed_pkey PRIMARY KEY (name);


--
-- Name: task_events task_events_pkey; Type: CONSTRAINT; Schema: public; Owner: ficus
--

ALTER TABLE ONLY public.task_events
    ADD CONSTRAINT task_events_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: ficus
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: tasks_embedding_hnsw; Type: INDEX; Schema: public; Owner: ficus
--

CREATE INDEX tasks_embedding_hnsw ON public.tasks USING hnsw (embedding public.vector_cosine_ops) WITH (m='16', ef_construction='64');


--
-- Name: tasks_ready_idx; Type: INDEX; Schema: public; Owner: ficus
--

CREATE INDEX tasks_ready_idx ON public.tasks USING btree (created_at) WHERE ((status = ANY (ARRAY['pending'::public.task_status, 'error'::public.task_status])) AND (locked_by IS NULL));


--
-- Name: tasks_running_idx; Type: INDEX; Schema: public; Owner: ficus
--

CREATE INDEX tasks_running_idx ON public.tasks USING btree (heartbeat_at) WHERE (status = 'running'::public.task_status);


--
-- Name: tasks_status_idx; Type: INDEX; Schema: public; Owner: ficus
--

CREATE INDEX tasks_status_idx ON public.tasks USING btree (status);


--
-- Name: tasks_tags_gin; Type: INDEX; Schema: public; Owner: ficus
--

CREATE INDEX tasks_tags_gin ON public.tasks USING gin (tags);


--
-- Name: task_events task_events_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ficus
--

ALTER TABLE ONLY public.task_events
    ADD CONSTRAINT task_events_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict SUSDVa32bgc9LcUSs1Brtur92rhLM3iaj1sRmXSDJcQaRU7YUFGMia8IIprRdVX

