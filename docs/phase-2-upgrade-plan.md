# Phase 2 Upgrade Plan: Channel Radar, Intelligence, Video Inventory & Lido Improvement Loop

**Codename:** `BCE-Factory v1.0 Upgrade`  
**Target Channel:** `@1995lido`  
**Status:** In Progress  

---

## 1. Executive Summary & Objective

The Buddhist Community Engagement Factory (`BCE-Factory`) operates under the core directive: **"Do not confuse automation with autonomy."**
The current Phase 1 MVP & Phase 2 Publishing Engine reliably discovers videos, generates mindful comments, verifies quality gates, and publishes/dry-runs comments for `@1995lido`.

This upgrade extends the factory from simple opportunistic video discovery to a structured intelligence ecosystem:
1. **Channel Radar (`channel_radar.py`)**: Continuously monitors Buddhist channels across Vietnamese and English spaces, classifying them into tiers (`A_MAJOR`, `B_STRONG`, `C_RISING`, `D_EMERGING`).
2. **Channel Intelligence (`channel_intelligence.py`)**: 3-layer analysis (Observation, Interpretation, Opportunity) to decode what works, why audiences engage, and how `@1995lido` can learn.
3. **Video Inventory & Priority Queue (`video_inventory.py`, `video_queue.py`)**: Systematically tracks channel videos and prioritizes high-impact engagement opportunities (fresh uploads on major channels, rising discussions).
4. **Community Intelligence (`community_intelligence.py`)**: Aggregates community sentiment, pain points, questions, and desired emotions across videos and channels.
5. **Lido Improvement Loop (`lido_improvement.py`)**: Produces actionable insights, content gap analysis, and content experimentation recommendations tailored for `@1995lido` (stored in DB and exported as Markdown reports).

---

## 2. Reused vs New Modules

### Reused & Preserved:
- `app_config.py`: Environment configuration and safety identity verification.
- `models.py`: Extended with Channel, ChannelIntelligence, LidoInsight schemas.
- `db_storage.py`: Schema extended with `channels`, `channel_intelligence`, and `lido_insights` tables; `videos` table updated with tracking timestamps and views.
- `discovery.py`: Retained for standalone keyword discovery; integrated with inventory.
- `transcript.py`: Captures video transcripts.
- `comments.py`: Reads community comments.
- `research.py`: Synthesizes video knowledge cards.
- `comment_generator.py`: Generates Reflective, Insightful, and Question candidates (Vietnamese and English).
- `quality.py`: Evaluates candidates against strict non-promotional and ethical quality gates.
- `language_detector.py`: Strict language detection (VI, EN, or UNCERTAIN).
- `youtube_publisher.py`: Dry-run and real publishing with strict channel identity guards.
- `report.py`: Extended with Channel Radar summary and Lido Improvement reporting.

### New Modules:
1. `channel_radar.py`
2. `channel_intelligence.py`
3. `video_inventory.py`
4. `video_queue.py`
5. `community_intelligence.py`
6. `lido_improvement.py`

---

## 3. Database Schema Migration

### Tables:
- `channels`:
  `channel_id (PK)`, `channel_name`, `channel_url`, `language`, `subscriber_count`, `video_count`, `tradition`, `tier`, `status`, `last_scanned_at`, `created_at`.
- `channel_intelligence`:
  `channel_id (PK)`, `content_strengths`, `audience_engagement_level`, `top_performing_topics`, `comment_community_vibe`, `lido_learnings`, `updated_at`.
- `videos` (extended):
  `video_id (PK)`, `channel_id`, `title`, `url`, `published_at`, `view_count`, `comment_count`, `priority_score`, `status`, `first_seen_at`, `last_seen_at`, `created_at`.
- `lido_insights`:
  `insight_id (PK)`, `date`, `category`, `observation`, `interpretation`, `opportunity_for_lido`, `priority`, `created_at`.

---

## 4. Execution Workflow (19-Step Upgrade Loop)

1. Radar scans/loads active monitored channels.
2. Filter channels by tier & active status.
3. Update channel intelligence (strengths, vibe, learnings).
4. Discover fresh videos from active monitored channels.
5. Ingest into Video Inventory (deduplicate against DB).
6. Rank videos via Priority Queue (tier, recency, velocity).
7. Select top 3–5 videos for daily workflow.
8. Extract metadata & transcripts.
9. Conduct video research & context analysis.
10. Read community comments & extract audience pain points.
11. Build Community Intelligence profile.
12. Detect discussion gap.
13. Generate 3 candidate comments (strict language matching).
14. Evaluate candidates through Quality Gate (0 self-promotion, 0 fake monk persona).
15. Select winning candidate.
16. Publish or Dry-run (respecting max 5 comments/day).
17. Store engagement & performance records in DB.
18. Generate Lido Improvement recommendations (Daily report).
19. Compile Daily Master Engagement & Radar Report.

---

## 5. Verification Strategy
- Backward compatibility: Existing 16 pytest tests must continue passing.
- New test suite `tests/test_phase2_upgrade.py`:
  - Channel Radar tiering & discovery test.
  - Channel Intelligence 3-layer card test.
  - Video Inventory deduplication & queue ranking test.
  - Community Intelligence pain point extraction test.
  - Lido Improvement Loop synthesis test.
- Full CLI dry-run test: `main.py daily --dry-run`.
