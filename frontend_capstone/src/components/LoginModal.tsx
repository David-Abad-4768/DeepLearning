import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/lib/authContext';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

export function LoginModal() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const [open, setOpen] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await login(username, password);
      setSuccess(t('login_success', { user: username }));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      open={open}
      onOpenChange={o => {
        setOpen(o);
        if (!o) {
          setError(null);
          setSuccess(null);
          setUsername('');
          setPassword('');
        }
      }}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          className="text-white">
          {t('login')}
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>{t('login')}</DialogTitle>
        </DialogHeader>
        <form
          onSubmit={handleSubmit}
          className="space-y-4 mt-4">
          {error && (
            <Alert variant="destructive">
              <AlertTitle>{t('error')}</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          {success && (
            <Alert>
              <AlertTitle>{t('success')}</AlertTitle>
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}
          <div>
            <Label htmlFor="li-username">{t('username')}</Label>
            <Input
              id="li-username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
            />
          </div>
          <div>
            <Label htmlFor="li-password">{t('password')}</Label>
            <Input
              id="li-password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={() => setOpen(false)}
              type="button">
              {t('cancel')}
            </Button>
            <Button
              type="submit"
              disabled={loading}>
              {loading ? t('logging_in') : t('login')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
