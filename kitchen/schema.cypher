CREATE CONSTRAINT book_id_unique IF NOT EXISTS
FOR (b:Book) REQUIRE b.book_id IS UNIQUE;
CREATE CONSTRAINT territory_id_unique IF NOT EXISTS
FOR (t:Territory) REQUIRE t.territory_id IS UNIQUE;
CREATE CONSTRAINT entity_slug_unique IF NOT EXISTS
FOR (e:Entity) REQUIRE e.slug IS UNIQUE;
CREATE CONSTRAINT meta_key_unique IF NOT EXISTS
FOR (m:Meta) REQUIRE m.key IS UNIQUE;
CREATE INDEX territory_level_idx IF NOT EXISTS
FOR (t:Territory) ON (t.level);
CREATE INDEX territory_book_idx IF NOT EXISTS
FOR (t:Territory) ON (t.book_id);
CREATE INDEX entity_group_idx IF NOT EXISTS
FOR (e:Entity) ON (e.group);
CREATE INDEX entity_name_idx IF NOT EXISTS
FOR (e:Entity) ON (e.canonical_name);
CREATE INDEX quarantine_term_idx IF NOT EXISTS
FOR (q:QuarantineTerm) ON (q.term);
CREATE FULLTEXT INDEX entity_fulltext IF NOT EXISTS
FOR (e:Entity) ON EACH [e.canonical_name, e.aliases_text];
MERGE (m1:Meta {key:"skeleton_frozen"}) SET m1.value = "false";
MERGE (m2:Meta {key:"freeze_date"}) SET m2.value = "";
MERGE (m3:Meta {key:"schema_version"}) SET m3.value = "2";
