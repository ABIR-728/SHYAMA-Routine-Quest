-- SHYAMA V20 cloud sync + private media
-- Project: SHYAMA Routine Quest
create table if not exists public.shyama_sync_records (
  sync_code text not null,
  kind text not null,
  record_id text not null,
  payload jsonb not null default '{}'::jsonb,
  updated_at bigint not null default 0,
  deleted boolean not null default false,
  primary key (sync_code, kind, record_id)
);
alter table public.shyama_sync_records enable row level security;

create policy "shyama_sync_select" on public.shyama_sync_records for select
using (sync_code = coalesce((current_setting('request.headers', true)::json->>'x-sync-code'),''));
create policy "shyama_sync_insert" on public.shyama_sync_records for insert
with check (sync_code = coalesce((current_setting('request.headers', true)::json->>'x-sync-code'),''));
create policy "shyama_sync_update" on public.shyama_sync_records for update
using (sync_code = coalesce((current_setting('request.headers', true)::json->>'x-sync-code'),'') )
with check (sync_code = coalesce((current_setting('request.headers', true)::json->>'x-sync-code'),'') );

insert into storage.buckets (id,name,public) values ('shyama-media','shyama-media',false) on conflict (id) do nothing;
alter table storage.objects enable row level security;
create policy "shyama_media_select" on storage.objects for select
using (bucket_id='shyama-media' and (storage.foldername(name))[1] = encode(digest(coalesce((current_setting('request.headers', true)::json->>'x-sync-code'),''),'sha256'),'hex'));
create policy "shyama_media_insert" on storage.objects for insert
with check (bucket_id='shyama-media' and (storage.foldername(name))[1] = encode(digest(coalesce((current_setting('request.headers', true)::json->>'x-sync-code'),''),'sha256'),'hex'));
create policy "shyama_media_update" on storage.objects for update
using (bucket_id='shyama-media' and (storage.foldername(name))[1] = encode(digest(coalesce((current_setting('request.headers', true)::json->>'x-sync-code'),''),'sha256'),'hex'))
with check (bucket_id='shyama-media' and (storage.foldername(name))[1] = encode(digest(coalesce((current_setting('request.headers', true)::json->>'x-sync-code'),''),'sha256'),'hex'));
