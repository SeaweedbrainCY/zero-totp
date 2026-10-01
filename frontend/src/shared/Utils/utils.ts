
export function domain_name_validator(domain_name: string): boolean {
  const valid = /^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$/;
  return valid.test(domain_name);
}

export function isDeviceMobile(): boolean {
  return window.innerWidth <= 768;
}

export function getCookie(name: string) {
  let ca: Array<string> = document.cookie.split(';');
  let caLen: number = ca.length;
  let cookieName = `${name}=`;
  let c: string;

  for (let i: number = 0; i < caLen; i += 1) {
    c = ca[i].replace(/^\s+/g, '');
    if (c.indexOf(cookieName) == 0) {
      return c.substring(cookieName.length, c.length);
    }
  }
  return '';
}

export function parseTags(json_tags: string): string[] {
  const tags_extracted = JSON.parse(json_tags);
  const tags: string[] = [];
  try {
    for (const tag of tags_extracted) {
      if (tag != null) {
        if (this.sanitize(tag) != null) {
          tags.push(this.sanitize(tag)!);
        }
      }
    }
  } catch {
    return [];
  }
  return tags;
}

export function getDomainFromURI(uri: string): string {
  if (!uri) return '';
  try {
    const parsedUrl = new URL(uri);
    if (parsedUrl.protocol !== 'http:' && parsedUrl.protocol !== 'https:') {
      return '';
    }
    return parsedUrl.hostname;
  } catch {
    return '';
  }
