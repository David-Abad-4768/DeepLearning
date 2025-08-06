// src/components/SignUpModal.tsx
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useSignup } from '@/hooks/useAuthMutation';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

export function SignupModal() {
  const { t } = useTranslation();
  const signupMut = useSignup();

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
      // Llamamos al endpoint /user/ para crear al usuario.
      await signupMut.mutateAsync({ username, password });
      // Si no hubo excepción, mostramos el mensaje de éxito.
      setSuccess(t('signup_success', { user: username }));
      // NOTA: no navegamos ni tocamos isLoggedIn aquí.
    } catch (err: any) {
      setError(err.message || t('error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      open={open}
      onOpenChange={o => {
        setOpen(o);
        // Al cerrar, reseteamos todos los estados
        if (!o) {
          setError(null);
          setSuccess(null);
          setUsername('');
          setPassword('');
        }
      }}>
      <DialogTrigger asChild>
        <Button
          size="sm"
          className="text-white">
          {t('signup')}
        </Button>
      </DialogTrigger>

      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>{t('signup')}</DialogTitle>
          <DialogDescription>{t('create_an_account')}</DialogDescription>
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
            <Label htmlFor="su-username">{t('username')}</Label>
            <Input
              id="su-username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
            />
          </div>

          <div>
            <Label htmlFor="su-password">{t('password')}</Label>
            <Input
              id="su-password"
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
              {loading ? t('creating') : t('create_account')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
