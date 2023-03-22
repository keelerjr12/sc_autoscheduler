import { Organization } from "./organization.model";

export interface ShellFlyingLine {
    id: number
    num: number
    start_date_time: string
    fly_go: number
    org: Organization;
}

export interface Duty {
    id: number
    duty_type_id: number
    name: string
}

export interface ShellDuty {
    id: number
    duty_id: number
    start_date_time: string
    end_date_time: string
    duty: Duty;
}