package com.project.mensageria.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "room_sub_categories")
public class RoomSubCategory {

    @Id
    @Column(length = 10)
    private String id;

    @Column(unique = true, nullable = false, length = 100)
    private String name;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}