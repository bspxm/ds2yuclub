-- 添加淘汰赛树形关系字段
ALTER TABLE badminton_tournament_match 
ADD COLUMN IF NOT EXISTS prev_match1_id INTEGER,
ADD COLUMN IF NOT EXISTS prev_match2_id INTEGER,
ADD COLUMN IF NOT EXISTS next_match_id INTEGER;

-- 添加外键约束（可选）
-- ALTER TABLE badminton_tournament_match 
-- ADD CONSTRAINT fk_prev_match1 FOREIGN KEY (prev_match1_id) REFERENCES badminton_tournament_match(id),
-- ADD CONSTRAINT fk_prev_match2 FOREIGN KEY (prev_match2_id) REFERENCES badminton_tournament_match(id),
-- ADD CONSTRAINT fk_next_match FOREIGN KEY (next_match_id) REFERENCES badminton_tournament_match(id);

-- 添加索引优化查询
CREATE INDEX IF NOT EXISTS idx_match_prev1 ON badminton_tournament_match(prev_match1_id);
CREATE INDEX IF NOT EXISTS idx_match_prev2 ON badminton_tournament_match(prev_match2_id);
CREATE INDEX IF NOT EXISTS idx_match_next ON badminton_tournament_match(next_match_id);

COMMENT ON COLUMN badminton_tournament_match.prev_match1_id IS '左上游比赛ID';
COMMENT ON COLUMN badminton_tournament_match.prev_match2_id IS '右上游比赛ID';
COMMENT ON COLUMN badminton_tournament_match.next_match_id IS '下游比赛ID（胜者进入）';
