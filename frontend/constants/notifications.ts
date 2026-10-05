import {
  DollarSignIcon,
  FlagIcon,
  MailWarningIcon,
  PackageCheckIcon,
  SparklesIcon,
  UserCheckIcon,
  XCircleIcon,
  type LucideIcon,
} from "lucide-react"

// The badge shows the unread count up to this, then "9+".
export const MAX_BADGE_COUNT = 9
// After a dropped live stream, wait this long before reconnecting, doubling up to the maximum.
export const RECONNECT_MS = 2000
export const MAX_RECONNECT_MS = 60000

// How each kind the services send (prepza_common.notifications.NotificationKind) looks: its
// icon, and whether it's a problem to act on (shown in red).
export const NOTIFICATION_LOOKS: Record<
  string,
  { icon: LucideIcon; alert: boolean }
> = {
  question_flagged: { icon: FlagIcon, alert: false },
  question_fixed: { icon: SparklesIcon, alert: false },
  referral_rewarded: { icon: DollarSignIcon, alert: false },
  auto_top_up_charged: { icon: DollarSignIcon, alert: false },
  auto_top_up_failed: { icon: DollarSignIcon, alert: true },
  candidate_finished: { icon: UserCheckIcon, alert: false },
  invite_undelivered: { icon: MailWarningIcon, alert: true },
  interview_ready: { icon: PackageCheckIcon, alert: false },
  interview_cancelled: { icon: XCircleIcon, alert: true },
}
