// src/components/ThemeIcon.jsx

const ThemeIcon = ({ theme }) => {
  return (
    <div
      data-theme={theme}
      className="w-7 h-7 rounded-[15%] bg-base-100 flex items-center justify-center border border-base-content/20 shrink-0"
      style={{ position: "relative" }}
    >
      <div className="flex flex-wrap w-5 h-5 gap-[2px]">
        <span className="w-[9px] h-[9px] rounded-[30%] bg-primary block"></span>
        <span className="w-[9px] h-[9px] rounded-[30%] bg-secondary block"></span>
        <span className="w-[9px] h-[9px] rounded-[30%] bg-accent block"></span>
        <span className="w-[9px] h-[9px] rounded-[30%] bg-neutral block"></span>
      </div>
    </div>
  );
};

export default ThemeIcon;
