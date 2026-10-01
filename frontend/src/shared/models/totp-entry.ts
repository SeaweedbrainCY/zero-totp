export interface TOTPEntry {
  name: string;
  uri: string;
  secret: string;
  color: string;
  favicon: boolean;
  tags: string[];
}

const VALID_COLORS = new Set(['success', 'danger', 'info', 'warning']);

export function TOTPEntryToJSON(entry: TOTPEntry): string {
  return JSON.stringify(entry)
}

export function TOTPEntryFromJSON(jsonEntry: string): TOTPEntry {
  const totpEntryDefault: TOTPEntry = {
    name: 'Error',
    uri: '',
    secret: '',
    color: 'info',
    favicon: false,
    tags: [],
  };

  let raw: unknown;

  try {
    raw = JSON.parse(jsonEntry);
  } catch {
    return totpEntryDefault;
  }

  if (typeof raw !== 'object' || raw === null || Array.isArray(raw)) {
    return totpEntryDefault
  }

  const r = raw as Record<string, unknown>;

  return {
    name: typeof r['name'] === 'string' ? r['name'] : totpEntryDefault.name,
    uri: typeof r['uri'] === 'string' ? r['uri'] : totpEntryDefault.uri,
    secret: typeof r['secret'] === 'string' ? r['secret'] : totpEntryDefault.secret,
    color: VALID_COLORS.has(r['color'] as string)
      ? r['color'] as TOTPEntry['color']
      : totpEntryDefault.color,
    favicon: typeof r['favicon'] === 'boolean' ? r['favicon'] : totpEntryDefault.favicon,
    tags: Array.isArray(r['tags']) && r['tags'].every(t => typeof t === 'string')
      ? r['tags']
      : totpEntryDefault.tags,
  };
}
