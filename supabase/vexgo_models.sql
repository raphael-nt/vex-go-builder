-- VEX GO Builder cloud models (run once in Supabase SQL editor, project pfzmugbrmadtykftdced (vex-go-builder))
-- Anyone who knows a space code can list and open its models; only the holder of the edit key can change or delete.
create table if not exists public.vexgo_models (
  id uuid primary key default gen_random_uuid(),
  space text not null check (space ~ '^[a-z0-9_-]{2,32}$'),
  name text not null check (length(name) between 1 and 80),
  data jsonb not null check (pg_column_size(data) < 400000),
  thumb text check (thumb is null or (length(thumb) < 120000 and thumb like 'data:image/%')),
  count int not null default 0,
  key_hash text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists vexgo_models_space on public.vexgo_models(space, updated_at desc);
alter table public.vexgo_models enable row level security;
revoke all on public.vexgo_models from anon, authenticated;

create or replace function public.vexgo_list(p_space text)
returns table(id uuid, name text, count int, thumb text, updated_at timestamptz)
language sql stable security definer set search_path = '' as $$
  select m.id, m.name, m.count, m.thumb, m.updated_at from public.vexgo_models m
  where m.space = lower(p_space) order by m.updated_at desc limit 200
$$;

create or replace function public.vexgo_get(p_id uuid)
returns jsonb language sql stable security definer set search_path = '' as $$
  select jsonb_build_object('id',m.id,'name',m.name,'data',m.data,'updated_at',m.updated_at) from public.vexgo_models m where m.id = p_id
$$;

create or replace function public.vexgo_save(p_id uuid, p_key text, p_space text, p_name text, p_data jsonb, p_thumb text)
returns uuid language plpgsql security definer set search_path = '' as $$
declare h text := encode(extensions.digest(coalesce(p_key,''),'sha256'),'hex'); r uuid;
begin
  if length(coalesce(p_key,'')) < 16 then raise exception 'bad key'; end if;
  if jsonb_typeof(p_data->'parts') <> 'array' or jsonb_array_length(p_data->'parts') > 3000 then raise exception 'bad model'; end if;
  if p_id is not null then
    update public.vexgo_models set name=p_name, data=p_data, thumb=p_thumb, count=jsonb_array_length(p_data->'parts'), updated_at=now()
      where id=p_id and key_hash=h returning id into r;
    if r is not null then return r; end if;
    if exists(select 1 from public.vexgo_models where id=p_id) then raise exception 'not owner'; end if;
  end if;
  insert into public.vexgo_models(space,name,data,thumb,count,key_hash)
    values(lower(p_space),p_name,p_data,p_thumb,jsonb_array_length(p_data->'parts'),h) returning id into r;
  return r;
end $$;

create or replace function public.vexgo_delete(p_id uuid, p_key text)
returns boolean language sql security definer set search_path = '' as $$
  with d as (delete from public.vexgo_models where id=p_id and key_hash=encode(extensions.digest(coalesce(p_key,''),'sha256'),'hex') returning 1)
  select exists(select 1 from d)
$$;

revoke all on function public.vexgo_list(text), public.vexgo_get(uuid), public.vexgo_save(uuid,text,text,text,jsonb,text), public.vexgo_delete(uuid,text) from public;
grant execute on function public.vexgo_list(text), public.vexgo_get(uuid), public.vexgo_save(uuid,text,text,text,jsonb,text), public.vexgo_delete(uuid,text) to anon, authenticated;
