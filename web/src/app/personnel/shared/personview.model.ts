export interface PersonView {
    id: number;
    name: string;
    assigned_org: string;
    quals: Map<string, string>;
}