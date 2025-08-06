import i18n from '@/lib/i18n';
import en from '@/lib/locales/en.json';
import es from '@/lib/locales/es.json';
import { describe, expect, it } from 'vitest';

describe('i18n configuration', () => {
  it('initializes with English by default', () => {
    // The default language (lng) is 'en'
    expect(i18n.language).toBe('en');

    // Pick a key that exists in en.json
    const sampleKey = Object.keys(en)[0]!;
    expect(i18n.t(sampleKey)).toBe((en as Record<string, string>)[sampleKey]);
  });

  it('falls back when a key is missing', () => {
    // A key that does not exist should return the key itself (by default behavior)
    expect(i18n.t('nonexistent.key')).toBe('nonexistent.key');
  });

  it('can switch to Spanish and retrieve correct translations', async () => {
    await i18n.changeLanguage('es');
    expect(i18n.language).toBe('es');

    // Pick a key that exists in es.json
    const sampleKey = Object.keys(es)[0]!;
    expect(i18n.t(sampleKey)).toBe((es as Record<string, string>)[sampleKey]);
  });

  it('escapes interpolation properly when needed', () => {
    // Assuming en.json has a key like:
    // "withHtml": "This has <strong>{{value}}</strong>"
    // and interpolation.escapeValue is false, so HTML is left intact
    const val = 'TEST';
    // Add a fake key on the fly for testing
    i18n.addResource('en', 'translation', 'withHtml', 'Hello <strong>{{value}}</strong>');
    const rendered = i18n.t('withHtml', { value: val });
    expect(rendered).toBe(`Hello <strong>${val}</strong>`);
  });
});
