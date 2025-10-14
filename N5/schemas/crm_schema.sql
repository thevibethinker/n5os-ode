-- CRM Hybrid System Schema
-- Purpose: Fast indexing + network intelligence
-- Source of Truth: Markdown files in Knowledge/crm/profiles/
-- Database Role: Index + relationships for fast queries

-- ============================================================================
-- INDIVIDUALS: Core contact index pointing to markdown
-- ============================================================================
CREATE TABLE IF NOT EXISTS individuals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Core Identifiers
    full_name TEXT NOT NULL,
    email TEXT,
    linkedin_url TEXT,
    
    -- Professional Context
    company TEXT,
    title TEXT,
    
    -- Categorization (from frontmatter lead_type)
    category TEXT CHECK(category IN (
        'FOUNDER',
        'INVESTOR', 
        'CUSTOMER',
        'COMMUNITY',
        'NETWORKING',
        'ADVISOR',
        'PARTNER',
        'OTHER'
    )),
    
    -- Status & Priority
    status TEXT CHECK(status IN (
        'active',
        'prospect',
        'dormant',
        'archived'
    )) DEFAULT 'active',
    
    priority TEXT CHECK(priority IN (
        'high',
        'medium',
        'low'
    )) DEFAULT 'medium',
    
    -- Tags (JSON array as TEXT for flexibility)
    tags TEXT, -- e.g., '["series-a", "saas", "enterprise"]'
    
    -- Temporal tracking
    first_contact_date TEXT,
    last_contact_date TEXT,
    
    -- KEY: Path to source of truth
    markdown_path TEXT NOT NULL UNIQUE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INTERACTIONS: Touchpoint history
-- ============================================================================
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    individual_id INTEGER NOT NULL,
    
    interaction_type TEXT CHECK(interaction_type IN (
        'meeting',
        'email',
        'call',
        'event',
        'linkedin',
        'other'
    )),
    
    interaction_date TEXT NOT NULL, -- ISO format YYYY-MM-DD
    context TEXT, -- Brief description
    meeting_path TEXT, -- Path to meeting folder if applicable
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (individual_id) REFERENCES individuals(id) ON DELETE CASCADE
);

-- ============================================================================
-- RELATIONSHIPS: Person-to-person connections
-- ============================================================================
CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_a_id INTEGER NOT NULL,
    person_b_id INTEGER NOT NULL,
    
    relationship_type TEXT CHECK(relationship_type IN (
        'introduced_by',
        'works_with',
        'colleagues',
        'invested_in',
        'advises',
        'mutual_connection',
        'other'
    )),
    
    context TEXT,
    discovered_date TEXT, -- When we discovered this connection
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (person_a_id) REFERENCES individuals(id) ON DELETE CASCADE,
    FOREIGN KEY (person_b_id) REFERENCES individuals(id) ON DELETE CASCADE,
    
    -- Prevent duplicates
    UNIQUE(person_a_id, person_b_id, relationship_type)
);

-- ============================================================================
-- ORGANIZATIONS: Lightweight company tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    domain TEXT,
    industry TEXT,
    stage TEXT, -- seed, series-a, series-b, etc.
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDIVIDUAL_ORGANIZATIONS: Employment/affiliation history
-- ============================================================================
CREATE TABLE IF NOT EXISTS individual_organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    individual_id INTEGER NOT NULL,
    organization_id INTEGER NOT NULL,
    role TEXT, -- Their title at this org
    start_date TEXT,
    end_date TEXT,
    is_current BOOLEAN DEFAULT 1,
    
    FOREIGN KEY (individual_id) REFERENCES individuals(id) ON DELETE CASCADE,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    
    UNIQUE(individual_id, organization_id, role)
);

-- ============================================================================
-- INDEXES: Optimize common queries
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_individuals_name ON individuals(full_name);
CREATE INDEX IF NOT EXISTS idx_individuals_company ON individuals(company);
CREATE INDEX IF NOT EXISTS idx_individuals_category ON individuals(category);
CREATE INDEX IF NOT EXISTS idx_individuals_status ON individuals(status);
CREATE INDEX IF NOT EXISTS idx_individuals_priority ON individuals(priority);
CREATE INDEX IF NOT EXISTS idx_individuals_last_contact ON individuals(last_contact_date);
CREATE INDEX IF NOT EXISTS idx_interactions_individual ON interactions(individual_id);
CREATE INDEX IF NOT EXISTS idx_interactions_date ON interactions(interaction_date);
CREATE INDEX IF NOT EXISTS idx_relationships_person_a ON relationships(person_a_id);
CREATE INDEX IF NOT EXISTS idx_relationships_person_b ON relationships(person_b_id);
CREATE INDEX IF NOT EXISTS idx_organizations_name ON organizations(name);

-- ============================================================================
-- TRIGGERS: Auto-update timestamps
-- ============================================================================
CREATE TRIGGER IF NOT EXISTS update_individuals_timestamp 
AFTER UPDATE ON individuals
FOR EACH ROW
BEGIN
    UPDATE individuals SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_organizations_timestamp 
AFTER UPDATE ON organizations
FOR EACH ROW
BEGIN
    UPDATE organizations SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- ============================================================================
-- VIEWS: Common query patterns
-- ============================================================================

-- High-priority contacts needing follow-up
CREATE VIEW IF NOT EXISTS priority_follow_ups AS
SELECT 
    i.id,
    i.full_name,
    i.company,
    i.category,
    i.last_contact_date,
    julianday('now') - julianday(i.last_contact_date) as days_since_contact,
    i.markdown_path
FROM individuals i
WHERE i.status = 'active' 
  AND i.priority = 'high'
  AND (i.last_contact_date IS NULL OR julianday('now') - julianday(i.last_contact_date) > 30)
ORDER BY days_since_contact DESC;

-- Network map: People grouped by organization
CREATE VIEW IF NOT EXISTS network_by_organization AS
SELECT 
    o.name as organization,
    COUNT(DISTINCT io.individual_id) as contact_count,
    GROUP_CONCAT(i.full_name, ', ') as contacts
FROM organizations o
JOIN individual_organizations io ON o.id = io.organization_id
JOIN individuals i ON io.individual_id = i.id
WHERE io.is_current = 1
GROUP BY o.id
ORDER BY contact_count DESC;

-- Recent interactions summary
CREATE VIEW IF NOT EXISTS recent_activity AS
SELECT 
    i.full_name,
    i.company,
    int.interaction_type,
    int.interaction_date,
    int.context,
    i.markdown_path
FROM interactions int
JOIN individuals i ON int.individual_id = i.id
WHERE julianday('now') - julianday(int.interaction_date) <= 30
ORDER BY int.interaction_date DESC;
