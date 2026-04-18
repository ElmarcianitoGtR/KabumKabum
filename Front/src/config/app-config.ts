import packageJson from "../../package.json";

const currentYear = new Date().getFullYear();

export const APP_CONFIG = {
  name: "KabumKabum",
  version: packageJson.version,
  copyright: `© ${currentYear}, KabumKabum.`,
  meta: {
    title: "KabumKabum -- Sistema de monitoreo de reactores nucleares",
    description:
      "Sistema desarrollado para el monitoreo de reactores de manera facil y elegante.",
  },
};
