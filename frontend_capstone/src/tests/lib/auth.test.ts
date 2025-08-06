// src/tests/lib/auth.test.ts
import { beforeEach, describe, expect, it, vi } from 'vitest';

var fakeDecode = vi.fn();

// 2) Mock jwt-decode before importing your module:
vi.mock('jwt-decode', () => ({
  default: fakeDecode,
}));

// 3) Now import *after* the mock call:
import { getUserFromCookie } from '@/lib/auth';

describe('getUserFromCookie & clearAuthCookie', () => {
  beforeEach(() => {
    // Reset JSDOM cookie store:
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: '',
    });
    fakeDecode.mockReset();
  });

  it('returns null when there is no access_token cookie', () => {
    document.cookie = 'other=foo; hello=world';
    expect(getUserFromCookie()).toBeNull();
  });

  it('returns null if jwt-decode throws (malformed token)', () => {
    fakeDecode.mockImplementation(() => {
      throw new Error('bad');
    });
    document.cookie = 'access_token=' + encodeURIComponent('bad.token');
    expect(getUserFromCookie()).toBeNull();
  });
});
