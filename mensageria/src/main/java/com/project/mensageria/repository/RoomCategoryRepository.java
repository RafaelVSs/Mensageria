package com.project.mensageria.repository;

import com.project.mensageria.entity.RoomCategory;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RoomCategoryRepository extends JpaRepository<RoomCategory, String> {
}
