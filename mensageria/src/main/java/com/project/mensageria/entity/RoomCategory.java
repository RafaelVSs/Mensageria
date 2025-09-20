package com.project.mensageria.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "room_categories")
public class RoomCategory {

    @Id
    @Column(length = 10)
    private String id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "sub_category_id")
    private RoomSubCategory subCategory;

    @Column(nullable = false, length = 100)
    private String name;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public RoomSubCategory getSubCategory() { return subCategory; }
    public void setSubCategory(RoomSubCategory subCategory) { this.subCategory = subCategory; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}