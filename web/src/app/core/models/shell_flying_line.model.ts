import { Organization } from "./organization.model";

export interface ShellFlyingLine {
    id: number
    num: number
    start_date_time: string
    fly_go: number
    org: Organization;
}