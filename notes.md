right now the cache contains
- items
  - id
  - name
  - folderID
  - organizationId
  - collectionIds
  - password
  - totp
- folders
  - id
  - name
- collections
  - id
  - name
  - organizationID
- organizations
  - id
  - name

I was hoping to keep things in a flat file but it seems painful in the long run
I should probably use sqlite to build out the relationships and make searching easier.

An item can be in one, none, or any of these: folder, organization, collection
Items can only be in one folder.
Items can only be in one organization.
Items can be in multiple collections.
A collection exists as part of one organization.
Item names can be shared even when sharing the same folder, organization, and colleciton(s).
Item ids are the only way to uniquly identify them.
Folders are user specific and do not relate directly to organizations/collections.

Browsing items can be approached in two ways using: organizations/collections or folders

Everything can be browsed using folders including items not related to organization/collections.
Best approach would be to narrow results by filtering organization and collection.

Thinking of making an interactive cli
- vim nav
- browse like file structure
- view for folders/items
- view for org/collection filter
- interactive login
- fzf search

Primary aim to make getting password/totp as fast and intuitive as possible.
This will not update/add items it will be readonly.
This will not display other fields it will only get password/totp.

