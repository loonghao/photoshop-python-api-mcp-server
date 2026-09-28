## v0.1.11 (2026-02-24)

### Fix

- redirect logging output from stdout to stderr

## [0.1.13](https://github.com/loonghao/photoshop-python-api-mcp-server/compare/v0.1.12...v0.1.13) (2026-09-28)


### Bug Fixes

* **ci:** attach release assets to the right tag without clobbering notes ([0d94c99](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/0d94c99752552b737ceb942573f29b70d9c0f666))
* **ci:** attach release assets with gh instead of softprops ([f008314](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/f008314c0683ca63eb4b5fe2a3a88123d36fbdd3))
* **ci:** drop package-name so release-please tags merged release PRs ([fa0ec37](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/fa0ec37367cc664dc3ca2df6d23aa025f6a2d4a7))
* **ci:** publish release outputs when called by Release Please ([f23dddd](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/f23ddddc2c9cd42da81a8608709080b48591a76f))
* handle UnitValue and float document dimensions ([863af0a](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/863af0aaa7aae211423bd79bac88441444315750))
* register and document the execute_jsx tool ([8dc41d5](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/8dc41d585a16470d6d2e8ba29c1b32fb88c74dc9))

## [0.1.12](https://github.com/loonghao/photoshop-python-api-mcp-server/compare/v0.1.11...v0.1.12) (2026-09-28)


### Bug Fixes

* **ci:** cut releases with GITHUB_TOKEN instead of an expired PAT ([a17a7ac](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/a17a7aca77337ebc9824e50d0bdce6c7eb947cd2))
* **ci:** drop pull-requests permission from reusable publish workflow ([142fdd7](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/142fdd7a42ee0f4602dde8684850bbe956638ad5))
* populate layers in get_active_document_info and add execute_jsx tool ([82de08d](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/82de08d0650726dee351a44e30219c7c909657de))

## v0.1.10 (2025-10-17)

### Fix

- correct mock paths in FastMCP initialization tests
- remove unsupported description and version parameters from FastMCP initialization

## v0.1.9 (2025-06-30)

### Fix

- **deps**: update dependency mcp to v1.10.1

## v0.1.8 (2025-06-18)

### Fix

- **deps**: update dependency mcp to v1.9.4

## v0.1.7 (2025-06-07)

### Fix

- **deps**: update dependency mcp to v1.9.3

## v0.1.6 (2025-05-26)

### Fix

- **deps**: update dependency mcp to v1.9.1

## v0.1.5 (2025-05-07)

### Fix

- **deps**: update dependency mcp to v1.7.1

## v0.1.4 (2025-05-07)

### Fix

- **deps**: update dependency photoshop-python-api to v0.24.1

## v0.1.3 (2025-05-02)

### Fix

- **deps**: update dependency mcp to v1.7.0

## v0.1.2 (2025-04-11)

### Fix

- standardize executable name to photoshop-mcp-server

## v0.1.1 (2025-04-11)

### Fix

- update PyPI publish workflow to use Linux runner

## v0.1.0 (2025-04-11)

### Feat

- implement dynamic tool registration for MCP server

### Fix

- use PhotoshopApp instance in Action Manager
