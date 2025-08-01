-- Main ConversationEntry table with nested sources
CREATE TABLE conversation_entry (
  entry_id STRING NOT NULL COMMENT 'unique identifier, combination of sessionId and interactionId',
  session_id STRING NOT NULL COMMENT 'session id as set by the client',
  interaction_id INT NOT NULL COMMENT 'sequential identifier for the interaction, used to order the conversation',
  date DATE NOT NULL COMMENT 'the date this entry was created, stored in central time',
  hour INT COMMENT 'the hour of the day this question was asked, stored in central time, assigned at consumption',
  question STRING NOT NULL COMMENT 'the question asked by the user',
  question_created TIMESTAMP WITH TIME ZONE NOT NULL COMMENT 'the time the question was asked',
  answer STRING NOT NULL COMMENT 'the answer given by the AI',
  answer_created TIMESTAMP WITH TIME ZONE NOT NULL COMMENT 'the time the answer was given',
  action STRING COMMENT 'the action field currently indicates the source of the answer, can be null, orders, or msa_agents',
  user_id STRING COMMENT 'the user id of the user who asked the question, can be null',
  location_id INT COMMENT 'the location id of the user who asked the question, can be null',
  region_id INT COMMENT 'the region which this store is currently assigned to',
  group_id INT COMMENT 'the group which this store is currently assigned to',
  district_id INT COMMENT 'the district which this store is currently assigned to',
  user_roles ARRAY<STRING> COMMENT 'the roles of the user who asked the question, can be null',
  sources ARRAY<STRUCT<
    name: STRING,
    score: FLOAT
  >> COMMENT 'the sources used for rag based search'
)
USING ICEBERG
PARTITIONED BY (date, hour)
TBLPROPERTIES (
  'format-version' = '2',
  'write.parquet.compression-codec' = 'zstd',
  'write.target-file-size-bytes' = '134217728',  -- 128MB
  'write.distribution-mode' = 'hash',
  'write.hash-distribution-columns' = 'session_id'
);