import { useTranslation } from "react-i18next";

export default function WelcomeSection({ className }: { className?: string }) {
  const { t } = useTranslation();
  return (
    <div
      className={`flex flex-col items-center justify-center h-full ${className ?? ""}`}
    >
      <h1 className="text-3xl font-semibold">
        {t("welcome_title", "Welcome to Finnisimo Chat V2")}
      </h1>
      <p className="mt-2 text-gray-500"></p>
    </div>
  );
}
