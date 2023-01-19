export interface Organization {
    id: number;
    name: string;
}

export interface Qualification {
    id: number;
    name: string;
}

export interface Person {
    id: number;
    first_name: string;
    middle_name: string;
    last_name: string;
    assigned_org: Organization | null;
    quals: Qualification[];
}