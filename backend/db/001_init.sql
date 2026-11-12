create extension if not exists vector;   -- adds the vector column type; already on in your project, this makes the script safe to re-run

create table public.documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,   -- owner; deleting a user removes their documents
  filename text not null,
  storage_path text not null,
  page_count int,
  status text not null default 'uploaded'
    check (status in ('uploaded', 'processing', 'ready', 'failed')),   -- lets the UI show progress and errors for bad or scanned PDFs
  error_message text,
  created_at timestamptz not null default now()
);

create table public.chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.documents(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,   -- repeated here so every vector search can filter by owner without a join
  chunk_index int not null,
  page_number int not null,   -- the source of every citation: never lose it during chunking
  content text not null,
  embedding vector(384) not null,   -- 384 is the output size of bge-small-en-v1.5
  created_at timestamptz not null default now()
);

create index chunks_document_id_idx on public.chunks (document_id);
create index chunks_user_id_idx on public.chunks (user_id);
create index chunks_embedding_idx on public.chunks
  using hnsw (embedding vector_cosine_ops);   -- speeds up nearest-neighbour search by cosine similarity

alter table public.documents enable row level security;   -- with RLS on and no policy, access is denied by default
alter table public.chunks enable row level security;

create policy documents_select_own on public.documents
  for select to authenticated using (user_id = (select auth.uid()));
create policy documents_insert_own on public.documents
  for insert to authenticated with check (user_id = (select auth.uid()));
create policy documents_delete_own on public.documents
  for delete to authenticated using (user_id = (select auth.uid()));
create policy chunks_select_own on public.chunks
  for select to authenticated using (user_id = (select auth.uid()));   -- users only read chunks; the backend writes them