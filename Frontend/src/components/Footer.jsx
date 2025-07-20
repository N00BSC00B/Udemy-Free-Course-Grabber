import { Github, Mail } from "lucide-react";
import { openUrl } from "../services/api";

const openGithub = async () => {
  try {
    await openUrl("https://github.com/N00BSC00B");
  } catch (error) {
    console.error("Failed to open GitHub:", error);
    // Fallback to window.open
    window.open(
      "https://github.com/N00BSC00B",
      "_blank",
      "noopener,noreferrer"
    );
  }
};
const Footer = () => (
  <footer className="w-full bg-base-200 border-t border-base-300 mt-10 pt-8 pb-4 px-2">
    <div className="max-w-[90vw] lg:max-w-[70vw] mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
      <div className="flex items-center gap-3">
        <span className="text-2xl font-bold tracking-wider text-primary">
          Udemy Free Course Grabber
        </span>
        <span className="ml-2 px-2 py-1 rounded bg-gradient-to-r from-primary to-accent text-white text-xs font-semibold shadow-md">
          Free & Fresh Daily
        </span>
      </div>
      <div className="flex items-center gap-4">
        <button
          onClick={openGithub}
          className="text-base-content hover:text-primary transition-colors"
          aria-label="GitHub"
        >
          <Github className="w-6 h-6" />
        </button>
        <a
          href="mailto:sayanbarma2004@gmail.com"
          className="text-base-content hover:text-primary transition-colors"
          aria-label="Email"
        >
          <Mail className="w-6 h-6" />
        </a>
      </div>
    </div>
    <div className="max-w-[90vw] lg:max-w-[70vw] mx-auto mt-4 text-center text-base-content/60 text-xs">
      &copy; {new Date().getFullYear()} Udemy Free Course Grabber &mdash;
      Crafted with <span className="text-error">♥</span> for lifelong learners.
    </div>
  </footer>
);

export default Footer;
