import { DeletePreparation } from "@/components/preparations/delete-preparation"
import { MembershipButton } from "@/components/preparations/membership-button"
import { ShareDialog } from "@/components/preparations/share-dialog"
import { VisibilityToggle } from "@/components/preparations/visibility-toggle"
import type { PreparationDetail } from "@/types/preparation"

export function PreparationShare({
  preparation,
}: {
  preparation: PreparationDetail
}) {
  const isOwner = preparation.access === "owner"
  const joined = preparation.access === "joined"
  const isPublic = preparation.visibility === "public"
  const showShare = isOwner || isPublic

  if (!showShare && !joined) {
    return null
  }

  return (
    <div className="flex shrink-0 items-center gap-3">
      {joined && <MembershipButton preparation={preparation} joined />}
      {isOwner && <VisibilityToggle preparation={preparation} />}
      {showShare && (
        <ShareDialog
          preparationId={preparation.id}
          title={preparation.title}
          isPublic={isPublic}
        />
      )}
      {isOwner && (
        <DeletePreparation preparationId={preparation.id} title={preparation.title} />
      )}
    </div>
  )
}

export function PreparationActions({
  preparation,
}: {
  preparation: PreparationDetail
}) {
  if (preparation.access !== "public") {
    return null
  }

  return <MembershipButton preparation={preparation} joined={false} />
}
