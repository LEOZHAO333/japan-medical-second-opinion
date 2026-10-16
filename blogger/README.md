# Blogger draft articles

Save complete HTML as `blogger/YYYY-MM-DD-lowercase-slug.html`, with a nonempty
`<title>` and one `<article>...</article>` containing the intended Blogger body.
Follow `MEDICAL-CONTENT-STANDARD.md`. No patient records or credentials belong here.

## Upload a draft

1. In repository Settings → Secrets and variables → Actions, configure:
   `BLOGGER_BLOG_ID`, `BLOGGER_CLIENT_ID`, `BLOGGER_CLIENT_SECRET`,
   `BLOGGER_REFRESH_TOKEN`. Agents secrets alone are insufficient.
2. The refresh token must come from the same OAuth client and an account permitted
   to manage the target blog, with `https://www.googleapis.com/auth/blogger` scope.
3. Open Actions → **Upload Blogger drafts** → **Run workflow**. Select `main`
   (or an up-to-date review branch) and enter the exact HTML file path.
4. The workflow validates the article, verifies Google OAuth and Blogger access,
   normalizes the public footer, then creates or updates a Blogger draft.
5. Only claim successful upload after the run summary says verified **DRAFT**.
   Review and publish manually in Blogger when editorial checks are complete.

Changed HTML files pushed to `main` or `automation/blogger-*` also trigger uploads.
Infrastructure-only changes do not upload existing articles. New review branches
must start from the updated main branch to include this workflow and script.

The uploader uses a source-path marker to update existing drafts, with exact-title
fallback for older unmarked drafts. Multiple matches, a different source with the
same title, or a matching live/scheduled post stop the upload for manual review.
Do not rename source files casually. Deleting a repository file does not delete a
Blogger post. No publish, revert or delete API is called. Avoid manually publishing
a draft during an upload; updates check status and include an ETag precondition.

## OAuth recovery and long-term setup

If the OAuth step fails with `invalid_grant`, the saved refresh token is expired,
revoked or otherwise no longer valid. For an External Google OAuth consent app left
in **Testing**, Google-issued refresh tokens can expire after seven days. Before
creating the replacement token, move the OAuth consent app to **In production** when
appropriate for this private publishing integration. Then authorize the same Google
account that manages the Blogger site using the same OAuth client and Blogger scope,
and replace the repository Actions secret `BLOGGER_REFRESH_TOKEN`.

If the OAuth step reports `invalid_client`, verify that `BLOGGER_CLIENT_ID` and
`BLOGGER_CLIENT_SECRET` belong to the same OAuth client that issued the refresh
token. Never paste client secrets, refresh tokens or access tokens into issues,
commits, workflow logs or chat messages.

Use Actions → **Check Blogger OAuth** to verify authorization and blog access without
creating or modifying a post. This check also runs weekly so expired/revoked access
is detected before a publishing batch. After replacing a token, run this health
check first, then rerun the failed Blogger draft upload.

If a network interruption follows a Blogger write, inspect Blogger and rerun:
discovery checks the source marker before creating another draft.

API references:
- https://developers.google.com/blogger/docs/3.0/reference/posts/insert
- https://developers.google.com/blogger/docs/3.0/reference/posts/list
- https://developers.google.com/blogger/docs/3.0/reference/posts/update
- https://developers.google.com/identity/protocols/oauth2
