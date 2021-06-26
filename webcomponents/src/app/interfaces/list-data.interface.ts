export interface AuditAreaList {
  audit_area?: string;
  remarks?: string;
}

export interface AuditUserList {
  audit_user_id?: string;
  role?: string;
  audit_company?: string;
  api_key?: string;
  api_secret?: string;
}
export interface AuditCompanyList {
  audit_company?: string;
}

export interface AuditTypeList {
  audit_type?: string;
  remarks?: string;
}

export interface AuditStageList {
  audit_stage?: string;
  remarks?: string;
}

export interface ClientList {
  client_name?: string;
  webiste?: string;
  pan?: string;
  cin?: string;
  constitution?: string;
  contacts?: ContactList[];
  locations?: LocationList[];
  other_records?: OtherRecordsList[];
}

export interface ContactList {
  name1?: string;
  email?: string;
  tel?: number;
  designation?: string;
}

export interface LocationList {
  loc_type?: string;
  address?: string;
}

export interface OtherRecordsList {
  record_name?: string;
}

export interface AuditAreaTemplate {
  title?: string;
  disabled?: boolean;
  audit_area_list?: AuditAreaTemplateTable[];
}

export interface AuditAreaTemplateTable {
  seq_no?: number;
  audit_area?: string;
}

export interface ChecklistTemplate {
  title?: string;
  disabled?: boolean;
  table_2?: ChecklistTemplateTable[];
}

export interface ChecklistTemplateTable {
  seq_no?: number;
  question?: string;
  response?: string;
}

export interface AuditStagesTemplate {
  title?: string;
  disabled?: boolean;
  audit_stages_list?: AuditStagesTemplateTable[];
}

export interface AuditStagesTemplateTable {
  seq_no?: number;
  audit_stage?: string;
}

export interface AuditFileEngagement {
  name?: string;
  audit_company?: string;
  audf_status?: string;
  client?: string;
  title?: string;
  pan?: string;
  earliest_start_date?: Date;
  last_finish_date?: Date;
  audit_type?: string;
  created_by?: string;
  reviewer?: string;
  coverage?: string;
  audit_period_from?: Date;
  audit_period_to?: Date;
  audit_area_list?: AuditFileAreaTemplateTable[];
  audit_stages_list?: AuditFileStagesTemplateTable[];
}

export interface AuditFileAreaTemplateTable {
  name?: string;
  parent?: string;
  seq_no?: number;
  audit_area?: string;
  is_complete?: boolean;
  target_date?: Date;
}

export interface AuditFileStagesTemplateTable {
  name?: string;
  parent?: string;
  seq_no?: number;
  audit_stage?: string;
  is_complete?: boolean;
  target_date?: Date;
}

export interface ChecklistEngagement {
  title?: string;
  audit_area?: string;
  audit_stage?: string;
  audit_company?: string;
  audit_file?: string;
  audit_period_from?: Date;
  audit_period_to?: Date;
  audit_type?: string;
  chkl_status?: string;
  client?: string;
  created_by?: string;
  creation?: string;
  assigned_to?: string;
  reviewer?: string;
  name?: string;
  pan?: string;
  target_date?: Date;
  question_details?: QuestionTemplateTable[];
}

export interface QuestionTemplateTable {
  name?: string;
  parent?: string;
  question?: string;
  response?: string;
  docstatus?: boolean;
}
