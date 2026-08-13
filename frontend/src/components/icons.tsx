// Inline SVG icons (stroke style, currentColor) — no emoji anywhere in the UI.
import type { SVGProps } from 'react'

type IconProps = SVGProps<SVGSVGElement> & { size?: number }

function base({ size = 20, ...props }: IconProps, children: React.ReactNode, viewBox = '0 0 24 24') {
  return (
    <svg
      width={size}
      height={size}
      viewBox={viewBox}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      {children}
    </svg>
  )
}

export const IconHome = (p: IconProps) =>
  base(p, (
    <>
      <path d="M3 10.5 12 3l9 7.5" />
      <path d="M5 9.5V21h14V9.5" />
      <path d="M9.5 21v-6h5v6" />
    </>
  ))

export const IconRoute = (p: IconProps) =>
  base(p, (
    <>
      <circle cx="6" cy="19" r="2.2" />
      <circle cx="18" cy="5" r="2.2" />
      <path d="M8.2 19H15a3 3 0 0 0 0-6H9a3 3 0 0 1 0-6h6.8" strokeDasharray="0.5 3.4" />
    </>
  ))

export const IconChat = (p: IconProps) =>
  base(p, (
    <>
      <path d="M21 12a8 8 0 0 1-8 8H4l2.2-3.1A8 8 0 1 1 21 12Z" />
      <path d="M9 11h.01M12.5 11h.01M16 11h.01" strokeWidth={2.6} />
    </>
  ))

export const IconChart = (p: IconProps) =>
  base(p, (
    <>
      <path d="M4 20V10" />
      <path d="M10 20V4" />
      <path d="M16 20v-7" />
      <path d="M22 20H2" />
    </>
  ))

export const IconSun = (p: IconProps) =>
  base(p, (
    <>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8" />
    </>
  ))

export const IconFlame = (p: IconProps) =>
  base(p, (
    <path d="M12 3c1 3-3.5 4.5-3.5 8.5a3.5 3.5 0 0 0 7 0c0-1.5-.7-2.6-1.5-3.5 2.8.6 5 2.9 5 6a7 7 0 1 1-14 0C5 8.5 9.5 6.5 12 3Z" />
  ))

export const IconMic = (p: IconProps) =>
  base(p, (
    <>
      <rect x="9" y="3" width="6" height="11" rx="3" />
      <path d="M5 11a7 7 0 0 0 14 0" />
      <path d="M12 18v3" />
    </>
  ))

export const IconPlay = (p: IconProps) => base(p, <path d="M7 4.5v15l13-7.5Z" fill="currentColor" stroke="none" />)

export const IconPause = (p: IconProps) =>
  base(p, (
    <>
      <rect x="6.5" y="4.5" width="4" height="15" rx="1" fill="currentColor" stroke="none" />
      <rect x="13.5" y="4.5" width="4" height="15" rx="1" fill="currentColor" stroke="none" />
    </>
  ))

export const IconVolume = (p: IconProps) =>
  base(p, (
    <>
      <path d="M4 9.5v5h3.5L12 19V5L7.5 9.5H4Z" fill="currentColor" stroke="none" />
      <path d="M15.5 9a4.2 4.2 0 0 1 0 6M18 6.5a8 8 0 0 1 0 11" />
    </>
  ))

export const IconExpand = (p: IconProps) =>
  base(p, <path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" />)

export const IconEye = (p: IconProps) =>
  base(p, (
    <>
      <path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12Z" />
      <circle cx="12" cy="12" r="3" />
    </>
  ))

export const IconEar = (p: IconProps) =>
  base(p, (
    <>
      <path d="M6.5 9a5.5 5.5 0 0 1 11 .5c0 3-2.5 3.8-3.7 5.7-.8 1.2-.8 2.3-1.6 3.3a3.6 3.6 0 0 1-5.7-.4" />
      <path d="M9.5 9.2a2.6 2.6 0 0 1 5 1c0 2-2.2 2.4-2.2 4.3" />
    </>
  ))

export const IconCheck = (p: IconProps) => base(p, <path d="m4.5 12.5 5 5 10-11" />)

export const IconX = (p: IconProps) => base(p, <path d="M6 6l12 12M18 6 6 18" />)

export const IconSpeaker = (p: IconProps) =>
  base(p, (
    <>
      <path d="M4 9.5v5h3.5L12 19V5L7.5 9.5H4Z" fill="currentColor" stroke="none" />
      <path d="M15 9.5a3.6 3.6 0 0 1 0 5M17.5 7a7 7 0 0 1 0 10" />
      <circle cx="19.5" cy="5" r="0.5" fill="currentColor" />
    </>
  ))

export const IconRocket = (p: IconProps) =>
  base(p, (
    <>
      <path d="M12 15c5-4 7-8.5 7-11.5C16.5 3.5 12 5.5 8 10.5L5 12l3.5.5L7 16l3.5-1Z" />
      <path d="M8.5 13.5c-1.5.8-2.5 2.5-3 5 2.5-.5 4.2-1.5 5-3" />
      <circle cx="14.5" cy="9.5" r="1.4" />
    </>
  ))

export const IconSuitcase = (p: IconProps) =>
  base(p, (
    <>
      <rect x="3.5" y="8" width="17" height="12" rx="2.5" />
      <path d="M9 8V6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2" />
      <path d="M3.5 13h17" />
    </>
  ))

export const IconCup = (p: IconProps) =>
  base(p, (
    <>
      <path d="M5 9h11v6a5 5 0 0 1-5 5h-1a5 5 0 0 1-5-5V9Z" />
      <path d="M16 10h1.5a2.5 2.5 0 0 1 0 5H16" />
      <path d="M8 5.5c0-1 .8-1 .8-2M11.5 5.5c0-1 .8-1 .8-2" />
    </>
  ))

export const IconChevronRight = (p: IconProps) => base(p, <path d="m9 5 7 7-7 7" />)

export const IconChevronDown = (p: IconProps) => base(p, <path d="m5 9 7 7 7-7" />)

export const IconClock = (p: IconProps) =>
  base(p, (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7v5l3.5 2" />
    </>
  ))

export const IconHeadphones = (p: IconProps) =>
  base(p, (
    <>
      <path d="M4 14v-2a8 8 0 0 1 16 0v2" />
      <rect x="3" y="13.5" width="4" height="7" rx="2" />
      <rect x="17" y="13.5" width="4" height="7" rx="2" />
    </>
  ))

export const IconReplay = (p: IconProps) =>
  base(p, (
    <>
      <path d="M4 5v5h5" />
      <path d="M4.8 10a8 8 0 1 1-1 5" />
    </>
  ))

export const IconBook = (p: IconProps) =>
  base(p, (
    <>
      <path d="M12 6.5C10 4.8 7 4.5 4 5v13c3-.5 6-.2 8 1.5 2-1.7 5-2 8-1.5V5c-3-.5-6-.2-8 1.5Z" />
      <path d="M12 6.5v13" />
    </>
  ))

export const IconPuzzle = (p: IconProps) =>
  base(p, (
    <path d="M9 4.5a2 2 0 1 1 4 0V6h3.5A1.5 1.5 0 0 1 18 7.5V11h-1.5a2 2 0 1 0 0 4H18v3.5a1.5 1.5 0 0 1-1.5 1.5H13v-1.5a2 2 0 1 0-4 0V20H5.5A1.5 1.5 0 0 1 4 18.5V15h1.5a2 2 0 1 0 0-4H4V7.5A1.5 1.5 0 0 1 5.5 6H9V4.5Z" />
  ))

export const IconPencil = (p: IconProps) =>
  base(p, (
    <>
      <path d="m14.5 5 4.5 4.5L8.5 20H4v-4.5L14.5 5Z" />
      <path d="m12.5 7 4.5 4.5" />
    </>
  ))

export const IconGlobe = (p: IconProps) =>
  base(p, (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M3.5 12h17M12 3.5c2.6 2.3 3.9 5.2 3.9 8.5s-1.3 6.2-3.9 8.5c-2.6-2.3-3.9-5.2-3.9-8.5S9.4 5.8 12 3.5Z" />
    </>
  ))

export const IconBuilding = (p: IconProps) =>
  base(p, (
    <>
      <path d="M4 21V5.5L12 3l8 2.5V21" />
      <path d="M2.5 21h19" />
      <path d="M8.5 21v-5h7v5" />
      <path d="M8.5 9h.01M12 9h.01M15.5 9h.01M8.5 12h.01M12 12h.01M15.5 12h.01" strokeWidth={2.4} />
    </>
  ))

export const IconTrend = (p: IconProps) =>
  base(p, (
    <>
      <path d="m3.5 16.5 5-5 3.5 3.5 7-7" />
      <path d="M15.5 8H19v3.5" />
    </>
  ))

export const IconWave = (p: IconProps) =>
  base(p, (
    <>
      <path d="M4 10v4M8 7v10M12 4v16M16 7v10M20 10v4" />
    </>
  ))

export const IconSparkle = (p: IconProps) =>
  base(p, <path d="M12 3l1.9 5.6L19.5 10l-5.6 1.9L12 17.5l-1.9-5.6L4.5 10l5.6-1.4L12 3Z" />)

export const IconMouth = (p: IconProps) =>
  base(p, (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M8 13.5c1.2 1.6 2.6 2.4 4 2.4s2.8-.8 4-2.4c-1.2-.6-2.6-.9-4-.9s-2.8.3-4 .9Z" />
    </>
  ))

export const IconPron = (p: IconProps) =>
  base(p, (
    <>
      <path d="M4 10v4M8 7v10M12 9v6M16 5v14M20 10v4" />
    </>
  ))

export const IconFluency = (p: IconProps) =>
  base(p, <path d="M3 12c2-4 4-4 6 0s4 4 6 0 4-4 6 0" />)

export const IconGrammar = (p: IconProps) =>
  base(p, (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="m8.5 12.5 2.5 2.5 5-6" />
    </>
  ))
