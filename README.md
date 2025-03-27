

> Author: arc/flamec

目标清单：重新构建 hsck 的“开发者工具”的后端部分。

## TODO LIST

### Random Utils

- [ ] 定时任务更新“app曝光”

### API EntryPoint

#### In Routes

> 此处列出的 API Entry 为所有写在原有后端的 Entry

- [ ] h5_apps.py
  - [ ] /upload_h5
  - [ ] /upload_icon
  - [ ] /upload_screenshot
  - [ ] /get_user_uploaded_apps
  - [ ] /get_app_detail
  - [ ] /update
  - [ ] /delete
  - [ ] /promote
  - [ ] /upload_donation_qrcode
  - [ ] /upload_screenshot_by_url
  - [ ] /upload_donation_qrcode_by_url

#### On use

>  此处列出的 APi Entry 为前端调用到的所有 Entry，不记录后端逻辑

- [ ] h5_apps
  - [ ] get_user_uploaded_apps
  - [ ] get_app_detail
  - [ ] update
  - [ ] delete
  - [ ] promote
- [ ] user
  - [ ] get_user_info
- [ ] static
  - [ ] h5_logo_data (get logo dynamic)

## Random Things

### 定时任务

> 作用：每日更新所有应用的曝光值
>
> 触发时间：4AM Everyday

处理方式简单粗暴，每天获取所有 APP 的 AppExposure 值，并更新为原来的 0.97 倍。

调用主数据库中的 `app_exposure` 表，使用外键关联 `h5_apps` 表中的 `h5_id` 值，
曝光值就是 `app_exposure` 表中的 `exposure` 值了。

| Table        | Column   | Notes                                          |
|--------------|----------|------------------------------------------------|
| app_exposure | h5_id    | Foreign Key to Table `h5_apps`, Column `h5_id` |
| app_exposure | exposure | contains the `exposure` value                  |

> Related Files: `models/app_exposure.py`, `services/h5_app_service.py`, `routes/h5_apps.py`

## API EntryPoint

### /upload_h5

> Method: `POST`
> Entry: `*/upload_h5`
> Return: `{'success': True | False, 'message': "*"}`

#### 业务流程

- check 是否存在有效载荷（data 非空）
- check 是否存在有效载荷（存在 `h5_name`, `description`, `category`, `deploy_url`）
- if fail 则返回 400
- if pass 则调用 `upload_h5_app` 上传(位于 `services/h5_apps_service.py`) & return
  - if throw exception
    - ValueError 则 print error & return
    - Expection 则 print error & return
- if throw exception
  - print error & return

### /upload_icon

> Method: `POST`
> Entry: `*/upload_h5`
> Return: `{'success': True | False, 'message': "*"}`

#### 业务流程

- check 是否上传了文件
  - if fail => 400
- check 文件名是否为空
  - if fail => 400
- check 是否存在“需要上传图标的应用 id”
  - if fail => 400
  - if pass => run `upload_h5_icon(file, id)` in `service/h5_apps_service.py:52`

### /upload_screenshot

> Method: `POST`
> Entry: `*/upload_screenshot`
> Return: `{'success': True | False, 'message': "*"}`

#### 业务流程

- check 是否上传了文件
  - if fail => 400
- check 是否存在截图序号
  - if fail => 400
- check 文件名是否为空
  - if fail => 400
- check 是否存在“需要上传图标的应用 id”
  - if fail => 400
  - if pass => run `upload_h5_screenshot(file, index, id)` in `service/h5_apps_service.py:68`
