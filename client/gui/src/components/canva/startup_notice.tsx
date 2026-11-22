import { useState } from "react"
import logo from "@/assets/logo_white.png"

// Shown once per launch. No storage: closing the app and reopening shows it again.
export default function StartupNotice() {
  const [open, setOpen] = useState(true)
  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center px-6"
      style={{
        background: "rgba(5, 4, 6, 0.88)",
        backdropFilter: "blur(7px)",
        WebkitBackdropFilter: "blur(7px)",
      }}
    >
      <div
        className="w-full max-w-[560px] overflow-hidden rounded-[14px] border font-mono"
        style={{
          background: "linear-gradient(180deg, #121016 0%, #0b090d 100%)",
          borderColor: "rgba(255, 70, 86, 0.34)",
          boxShadow:
            "0 0 0 1px rgba(255,255,255,0.03), 0 28px 80px rgba(0,0,0,0.7), 0 0 60px rgba(255,70,86,0.10)",
        }}
      >
        <div className="flex items-center gap-3 px-7 pt-7">
          <img
            src={logo}
            alt=""
            className="h-10 w-10 object-contain"
            style={{ filter: "brightness(1.9) contrast(1.05)" }}
          />
          <div className="flex flex-col leading-none">
            <span className="text-[13px] font-bold tracking-[0.22em] text-[#ece6e9]">ALICE</span>
            <span className="mt-1 text-[9.5px] tracking-[0.16em] text-[#7d747c]">
              OPERATIONS CONSOLE
            </span>
          </div>
        </div>

        <div className="px-7 pb-7 pt-6">
          <p className="text-[12.5px] leading-[1.75] text-[#cfc7cc]">
            made by <span className="text-[#ff4656]">fonfon</span> based on{" "}
            <span className="text-[#ece6e9]">nukerat</span>, i am not resposible for{" "}
            <span className="font-bold text-[#ff4656]">ANY SHIT</span> (any malicious
            activity) condoned, conducted, or executed with this software, provided as is
          </p>

          <div
            className="my-5 h-px w-full"
            style={{ background: "rgba(255,255,255,0.07)" }}
          />

          <p className="text-[12.5px] leading-[1.75] text-[#a89fa7]">
            much love, and havve fun <span className="text-[#ff4656]">:3</span>
          </p>

          <button
            type="button"
            onClick={() => setOpen(false)}
            className="mt-7 h-9 w-full cursor-pointer rounded-[8px] text-[11px] font-bold tracking-[0.16em] transition-colors"
            style={{
              background: "rgba(255, 70, 86, 0.14)",
              border: "1px solid rgba(255, 70, 86, 0.42)",
              color: "#ff8b95",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(255, 70, 86, 0.22)"
              e.currentTarget.style.color = "#ffd3d7"
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "rgba(255, 70, 86, 0.14)"
              e.currentTarget.style.color = "#ff8b95"
            }}
          >
            I UNDERSTAND
          </button>

          <p className="mt-4 text-center text-[9px] tracking-[0.14em] text-[#5f575f]">
            PROVIDED AS IS · NO WARRANTY · USE AT YOUR OWN RISK
          </p>
        </div>
      </div>
    </div>
  )
}
