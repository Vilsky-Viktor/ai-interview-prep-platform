"""no copies of other people's data: tool calls keep their arguments' names only and no result;
answers' blocks keep references (kind, ids, links), fetched again when a conversation opens

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-09
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE tool_calls
        SET result = NULL,
            arguments = COALESCE(
                (SELECT jsonb_agg(name ORDER BY name) FROM jsonb_object_keys(arguments) AS name),
                '[]'::jsonb
            )
        WHERE jsonb_typeof(arguments) = 'object'
        """
    )
    # The data blocks showed goes; their links (paths made of ids) stay. Their items' ids
    # weren't kept with the ids they need to be fetched again, so they show nothing now.
    op.execute(
        """
        UPDATE messages
        SET blocks = COALESCE(
            (
                SELECT jsonb_agg(
                    jsonb_build_object(
                        'kind', block -> 'kind',
                        'refs', '[]'::jsonb,
                        'links', COALESCE(block -> 'links', '[]'::jsonb)
                    )
                )
                FROM jsonb_array_elements(blocks) AS block
            ),
            '[]'::jsonb
        )
        WHERE blocks <> '[]'::jsonb
        """
    )


def downgrade() -> None:
    # What was emptied can't come back.
    pass
